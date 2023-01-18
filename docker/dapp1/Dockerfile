FROM debian

ARG PYCHARM_VERSION=2022.2
ARG PYCHARM_BUILD=2022.2.1

RUN apt-get update && apt-get install --no-install-recommends -y python3 python3-dev python3-setuptools python3-pip gcc git openssh-client less wget gnupg2 curl libxtst-dev libxext-dev libxrender-dev libfreetype6-dev libfontconfig1 libgtk2.0-0 libxslt1.1 libxxf86vm1 && rm -rf /var/lib/apt/lists/* && useradd -ms /bin/bash developer
RUN wget https://packages.erlang-solutions.com/erlang-solutions_2.0_all.deb && dpkg -i erlang-solutions_2.0_all.deb && apt update && apt install esl-erlang -y && apt install elixir -y

ARG pycharm_source=https://download.jetbrains.com/python/pycharm-community-${PYCHARM_BUILD}.tar.gz
#ARG pycharm_source=https://download.jetbrains.com/python/pycharm-professional-${PYCHARM_BUILD}.tar.gz
ARG pycharm_local_dir=.PyCharmCE${PYCHARM_VERSION}

WORKDIR /opt/pycharm

RUN curl -fsSL $pycharm_source -o /opt/pycharm/installer.tgz && tar --strip-components=1 -xzf installer.tgz && rm installer.tgz

USER developer
ENV HOME /home/developer

RUN mkdir /home/developer/.PyCharm && ln -sf /home/developer/.PyCharm /home/developer/$pycharm_local_dir

#RUN /opt/pycharm/bin/pycharm.sh installPlugins org.elixir_lang
#RUN /opt/pycharm/bin/pycharm.sh installPlugins net.ashald.envfile


CMD [ "/opt/pycharm/bin/pycharm.sh" ]