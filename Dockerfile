# 1. Base Image
FROM neurodebian:latest

# 2. Environment Setup
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

# 3. Install System Dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    curl \
    ca-certificates \
    octave \
    # Neuroimaging tools will be installed in the next step to keep it organized
    # gnupg is expected to be in neurodebian, if not, it would be added here
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# 4. Install Neuroimaging Tools & Set Environment Variables

# FSL
RUN apt-get update && \
    apt-get install -y --no-install-recommends fsl-core \
 && apt-get clean && rm -rf /var/lib/apt/lists/*
ENV FSLDIR=/usr/share/fsl/5.0 
# NeuroDebian typically installs FSL in a versioned directory.
# If fsl-core installs to a different top-level dir (e.g. /usr/share/fsl without /5.0)
# this ENV var would need adjustment. /usr/share/fsl/5.0 is a common default.
ENV FSLOUTPUTTYPE=NIFTI_GZ
ENV PATH=$FSLDIR/bin:$PATH
ENV FSLMULTIFILEQUIT=TRUE
ENV POSSUMDIR=$FSLDIR
ENV LD_LIBRARY_PATH=${FSLDIR}/lib:$LD_LIBRARY_PATH

# AFNI
RUN apt-get update && \
    apt-get install -y --no-install-recommends afni \
 && apt-get clean && rm -rf /var/lib/apt/lists/*
ENV AFNI_DIR=/usr/lib/afni/bin
ENV PATH=$AFNI_DIR:$PATH

# ANTS (ANTsX)
RUN apt-get update && \
    apt-get install -y --no-install-recommends ants \
 && apt-get clean && rm -rf /var/lib/apt/lists/*
ENV ANTSPATH=/usr/lib/ants
ENV PATH=$ANTSPATH:$PATH

# 5. Copy Repository Contents
COPY . /opt/project

# Set the working directory
WORKDIR /opt/project

# 6. Install Python Dependencies
RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

# 7. Permissions (if necessary)
# No specific script execution mentioned for now, can be added later if needed.
# RUN chmod +x /opt/project/your_script.py

# 8. Cleanup (already done after each apt-get install block to reduce layer size)

# Expose any ports if necessary (not specified)
# ENTRYPOINT or CMD (not specified)
