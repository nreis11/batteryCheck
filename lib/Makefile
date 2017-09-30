#
# Build static and shared libraries for raspidmx
# MODIFIED copy of original raspidmx for battery check code!
# Many original files are omitted. Shared library files are commented out
#

LIB=raspidmx

OBJS=../common/loadpng.o ../common/imageLayer.o ../common/image.o

CFLAGS+=-Wall -g -O3 -I../common $(shell libpng-config --cflags)
LDFLAGS+=-L/opt/vc/lib/ -lbcm_host -lm $(shell libpng-config --ldflags)

INCLUDES+=-I/opt/vc/include/ -I/opt/vc/include/interface/vcos/pthreads -I/opt/vc/include/interface/vmcs_host/linux

all: $(LIB)

%.o: %.c
	@rm -f $@
	$(CC) $(CFLAGS) $(INCLUDES) -g -c $< -o $@ -Wno-deprecated-declarations

$(LIB): $(OBJS)
	$(AR) rcs lib$(LIB).a $(OBJS)
	#$(CC) -shared -Wl,-soname,lib$(LIB).so.1 $(LDFLAGS) -o lib$(LIB).so.1 $(OBJS)

# TODO: move to debian package
	#ln -sfv lib$(LIB).so.1 lib$(LIB).so

clean:
	@rm -f $(OBJS)
	#@rm -f lib$(LIB).so*
	@rm -f lib$(LIB).a
