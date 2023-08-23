# Use the standard version of the Python runtime as the base image
FROM python:3.10.12

# Install required packages and add LLVM keys and repository
RUN apt-get update && apt-get install -y wget software-properties-common lsb-release gnupg && \
    wget -O - https://apt.llvm.org/llvm-snapshot.gpg.key | apt-key add - && \
    echo "deb http://apt.llvm.org/$(lsb_release -cs)/ llvm-toolchain-$(lsb_release -cs)-16 main" >> /etc/apt/sources.list && \
    apt-get update

# Install system dependencies including clang and libclang-dev
RUN apt-get install -y \
    gcc \
    g++ \
    clang-16 \
    libclang-16-dev \
    gcovr \
    && rm -rf /var/lib/apt/lists/*

# Set environment variable for clang
ENV CC=/usr/bin/clang-16
# Setting the LIBCLANG_PATH to where Docker usually places the shared library
ENV LIBCLANG_PATH=/usr/lib/llvm-16/lib

# Set the environment variable for the display
ENV DISPLAY=host.docker.internal:0.0

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install the Python dependencies
RUN pip install -r requirements.txt

# Change working directory to the GUI directory inside the container
WORKDIR /app/GUI

# Run the app as the default command
CMD ["python", "main.py"]
