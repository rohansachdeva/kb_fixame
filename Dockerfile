FROM kbase/sdkbase2:python
MAINTAINER Rohan Sachdeva
# -----------------------------------------
# In this section, you can install any system dependencies required
# to run your App.  For instance, you could place an apt-get update or
# install line here, a git checkout to download code, or run any other
# installation scripts.


# To install all the dependencies
RUN apt-get update && apt-get install -y samtools wget build-essential zlib1g-dev libbz2-dev

RUN pip install Cython && pip install biopython regex psutil xopen pandas pysam

RUN git clone https://gist.github.com/rohansachdeva/86bcf2cc974b2c72235638f5e5df043d && \
	mv 86bcf2cc974b2c72235638f5e5df043d FixAME && \
	chmod a+x FixAME/FixAME.py && \
	mv FixAME /kb/deployment/bin && \
	wget 'https://downloads.sourceforge.net/project/bbmap/BBMap_38.76.tar.gz?r=https%3A%2F%2Fsourceforge.net%2Fprojects%2Fbbmap%2Ffiles%2Flatest%2Fdownload&ts=1581407830' -O bbmap.tar.gz && \
	tar zxvf bbmap.tar.gz && \
	chmod -R a+x bbmap/* && \
	cp -r bbmap/* /kb/deployment/bin #&& \

	apt-get purge -y wget build-essential  && \
	apt-get autoremove -y && \
	apt-get clean

# -----------------------------------------

ENV PATH /kb/deployment/bin/bbmap:$PATH

COPY ./ /kb/module
RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module

WORKDIR /kb/module

RUN make all

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]