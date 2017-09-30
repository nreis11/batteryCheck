//-------------------------------------------------------------------------
//
// The MIT License (MIT)
//
// Copyright (c) 2013 Andrew Duncan
//
// Permission is hereby granted, free of charge, to any person obtaining a
// copy of this software and associated documentation files (the
// "Software"), to deal in the Software without restriction, including
// without limitation the rights to use, copy, modify, merge, publish,
// distribute, sublicense, and/or sell copies of the Software, and to
// permit persons to whom the Software is furnished to do so, subject to
// the following conditions:
//
// The above copyright notice and this permission notice shall be included
// in all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
// OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
// MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
// IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
// CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
// TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
// SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
//
//-------------------------------------------------------------------------
//
// September 2017 Edit:
//
// This copy of the software has been modified to provide a battery
// display function for use with RetroPie.
//
//-------------------------------------------------------------------------

#define _GNU_SOURCE

#include <assert.h>
#include <ctype.h>
#include <signal.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#include "imageLayer.h"
#include "loadpng.h"

#include "bcm_host.h"

//-------------------------------------------------------------------------

#define NDEBUG

//-------------------------------------------------------------------------

const char *program = NULL;

//-------------------------------------------------------------------------

static void signalHandler(int signalNumber) { /* Do nothing */ }

//-------------------------------------------------------------------------

void usage(void)
{
    fprintf(stderr, "Usage: %s ", program);
    fprintf(stderr, "[-d <number>] [-l <layer>] ");
    fprintf(stderr, "[-x <offset>] [-y <offset>]");
    fprintf(stderr, "[-s <stepSize>] [-t <displayTime>] <file.png>\n");
    fprintf(stderr, "    -d - Raspberry Pi display number (default: 0)\n");
    fprintf(stderr, "    -l - DispmanX layer number (default: 10500)\n");
    fprintf(stderr, "    -x - offset (pixels from the left) (default: 32)\n");
    fprintf(stderr, "    -y - offset (pixels from the top) (default: 32)\n");
    fprintf(stderr, "    -s - stepsize (pixels per update) (default: 32)\n");
    fprintf(stderr, "    -t - icon display time (seconds) (default: 3)\n");


    exit(EXIT_FAILURE);
}

//-------------------------------------------------------------------------

int main(int argc, char *argv[])
{
    uint32_t displayNumber = 0;
    int32_t layer = 10500;	// This default value puts the image above emulationstation
    int32_t currentX = 0;	// Variable used to slide image along x axis
    int32_t xOffset = 32;	// Determines where image slides to, horizontally, measured from the left side of the screen
    int32_t yOffset = 32;	// Determines where image slides to, vertically, measured from the top of the screen
    int32_t stepSize = 32;	// How fast the image slides from offscreen
    int32_t dispTime = 3;	// Number of seconds to keep the battery icon on-screen
    int32_t offscreenX = -1;	// Stores the x-position needed to hide the image off the left side of the screen

    program = basename(argv[0]);

    //---------------------------------------------------------------------

    int opt = 0;

    while ((opt = getopt(argc, argv, "l:x:y:s:t:")) != -1)
    {
        switch(opt)
        {

        case 'd':

            displayNumber = strtol(optarg, NULL, 10);
            break;

        case 'l':

            layer = strtol(optarg, NULL, 10);
            break;

        case 'x':

            xOffset = strtol(optarg, NULL, 10);
            break;

        case 'y':

            yOffset = strtol(optarg, NULL, 10);
            break;

        case 's':
	    stepSize = strtol(optarg, NULL, 10);
	    break;

        case 't':
	    dispTime = strtol(optarg, NULL, 10);
	    break;

        default:

            usage();
            break;
        }
    }

    //---------------------------------------------------------------------

    if (optind >= argc)
    {
        usage();
    }

    //---------------------------------------------------------------------

    if (signal(SIGINT, signalHandler) == SIG_ERR)
    {
        perror("installing SIGINT signal handler");
        exit(EXIT_FAILURE);
    }

    //---------------------------------------------------------------------

    if (signal(SIGTERM, signalHandler) == SIG_ERR)
    {
        perror("installing SIGTERM signal handler");
        exit(EXIT_FAILURE);
    }

    //---------------------------------------------------------------------

    bcm_host_init();

    //---------------------------------------------------------------------

    DISPMANX_DISPLAY_HANDLE_T display
        = vc_dispmanx_display_open(displayNumber);
    assert(display != 0);

    //---------------------------------------------------------------------

    DISPMANX_MODEINFO_T info;
    int result = vc_dispmanx_display_get_info(display, &info);
    assert(result == 0);

    //---------------------------------------------------------------------

    IMAGE_LAYER_T imageLayer;
    if (loadPng(&(imageLayer.image), argv[optind]) == false)
    {
        fprintf(stderr, "unable to load %s\n", argv[optind]);
    }
    createResourceImageLayer(&imageLayer, layer);

    // Determine where 'offscreen' should be +1 frame of animation
    offscreenX = stepSize - imageLayer.image.width; 	// x-position of the first frame of the slide animation

    // Clamp the value (effectively disables the animation)
    if(offscreenX > xOffset){
	offscreenX = xOffset;
    }

    //---------------------------------------------------------------------

    DISPMANX_UPDATE_HANDLE_T update = vc_dispmanx_update_start(0);
    assert(update != 0);

    // Draw inital image just offscreen
    addElementImageLayerOffset(&imageLayer,
                               offscreenX,
                               yOffset,
                               display,
                               update);

    result = vc_dispmanx_update_submit_sync(update);
    assert(result == 0);

    //---------------------------------------------------------------------

    // Create loop for battery display sliding onto the screen
    currentX = offscreenX;
    while(currentX < xOffset){
	
	// Update x position
	currentX += stepSize;

	// Clamp value
	if(currentX > xOffset){ 
		currentX = xOffset;
	}

	update = vc_dispmanx_update_start(0);
	assert(update != 0);

	moveImageLayer(&imageLayer, currentX, yOffset, update);

	result = vc_dispmanx_update_submit_sync(update);
	assert(result == 0);

	usleep(16667);

    }

    // Pause a moment so the user can read the display
    sleep( dispTime );

    // Now loop back and slide the image out of view
    while(currentX > (offscreenX + stepSize)){
	
	// Update x position
	currentX -= stepSize;

	update = vc_dispmanx_update_start(0);
	assert(update != 0);

	moveImageLayer(&imageLayer, currentX, yOffset, update);

	result = vc_dispmanx_update_submit_sync(update);
	assert(result == 0);

	usleep(16667);

    }

    //---------------------------------------------------------------------

    destroyImageLayer(&imageLayer);

    //---------------------------------------------------------------------

    result = vc_dispmanx_display_close(display);
    assert(result == 0);

    //---------------------------------------------------------------------

    return 0;
}

