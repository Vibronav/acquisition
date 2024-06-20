FROM ubuntu:22.04


# Set environment variables to avoid interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive
ENV SSH_USERNAME=ubuntu
ENV PASSWORD=changeme


# Install package dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    openssh-server \
    iputils-ping \
    telnet \
    iproute2 \
    libsndfile1-dev \
    alsa-utils \
	libasound2 \
	libasound2-plugins \
	pulseaudio \
	pulseaudio-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Create the privilege separation directory and fix permissions
RUN mkdir -p /run/sshd \
    && chmod 755 /run/sshd

# Check if the user exists before trying to create it
RUN if ! id -u $SSH_USERNAME > /dev/null 2>&1; then useradd -ms /bin/bash $SSH_USERNAME; fi

# Set up SSH configuration
RUN mkdir -p /home/$SSH_USERNAME/.ssh && chown $SSH_USERNAME:$SSH_USERNAME /home/$SSH_USERNAME/.ssh \
    && echo "PasswordAuthentication yes" >> /etc/ssh/sshd_config \
    && echo "PermitRootLogin no" >> /etc/ssh/sshd_config

# Copy the script to configure the user's password and authorized keys
COPY configure-ssh-user.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/configure-ssh-user.sh

# Expose SSH port
EXPOSE 22

CMD /usr/local/bin/configure-ssh-user.sh 



# ENV HOME /home/$SSH_USERNAME
# RUN useradd --create-home --home-dir $HOME pulseaudio \
# 	

# WORKDIR $HOME
# USER pulseaudio

# COPY default.pa /etc/pulse/default.pa
# COPY client.conf /etc/pulse/client.conf
# COPY daemon.conf /etc/pulse/daemon.conf

# CMD pulseaudio --log-level=4 --log-target=stderr -v





