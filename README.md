# HandMimicArm
Códigos desenvolvidos para projetos com o braço robô


## Tabela de conteúdos
- [Introdução](#introdução)
- [Requisitos](#requisitos)
- [Estrutura do projeto](#estrutura-do-projeto)
  - [Arduino](#arduino)
  - [Python](#python)
- [Aplicação](#aplicação-e-como-utilizar)
- [Documentação](#documentação-e-referências)
- [Licença](#licença)


## Introdução
O projeto HandMimicArm permite que você controle um braço robótico de 4 graus de liberdade (DOF) usando gestos da mão detectados por meio de uma webcam e um script Python em seu PC local.
Este projeto combina técnicas de visão computacional, um Arduino e um braço com 4 servo-motores.
Este projeto utiliza as bibliotecas MediaPipe para a detecção de pontos de referência da mão, a OpenCV para processamento de imagens e a pyFirmata2 para comunicação com o Arduino.
Para a realização deste projeto, utilizamos o [braço robótico de 4 DOF da RoboCore](https://www.robocore.net/robotica-robocore/braco-robotico-roboarm) em conjunto com um Arduino Uno.


## Requisitos
Para executar este projeto, você precisará dos seguintes itens:
- Arduino
- Bibliotecas Python (MediaPipe, OpenCV, pyFirmata2)
- Braço robótico de 4 DOF da RoboCore (RoboArm)
- Python 3.9
- Sketch "StandarFirmata" para a ArduinoIDE
- WebCam ou outra câmera


## Estrutura do projeto


### Arduino


### Python


## Aplicação e como utilizar
Para utilizar o projeto, é preciso seguir os seguintes passos:
1. **Clone o repositório do projeto**:
```bash
git clone https://github.com/Fundacao-Asimo/RoboArm.git
```
2. **Instale Python em seu computador**:
Caso ainda não tenha instalado, é possível encontrar informações por meio do seguinte link: [download Python](https://www.python.org/downloads/)
3. **Instale as bibliotecas necessárias em Python**:
```bash
pip install mediapipe opencv-python pyfirmata2
```
4. **Carregue o sketch "StandardFirmata" em seu Arduino pela Arduino IDE**:
```bash
```
5. **Faça as conexões de seu braço robótico**:
```bash
```
6. **Execute o script Python que controlorá o braço robótico com base em seus gestos de mão**:
```bash
python src/main.py
```
7. **Faça os gestos com a mão para controlar a rotação da base, a altura, a extensão e a abertura da garra do braço robótico**


## Documentação e referências
- [Braço robótico](https://www.robocore.net/robotica-robocore/braco-robotico-roboarm): neste link, estão todas as informações sobre o braço robótico utilizado durante o projeto
- [Inspiração para o projeto](https://www.youtube.com/watch?v=gdOV1OYF1Go): neste link, é encontrada a inspiração inicial para a realização do projeto
- [MediaPipe](https://developers.google.com/mediapipe): aqui estão mais informações sobre a biblioteca MediaPipe para Python
- [OpenCV](https://opencv.org/): aqui estão mais informações sobre a biblioteca OpenCV para Python
- pyFirmata: aqui estão mais informações sobre a biblioteca pyFirmata2 para Python

## Licença

Este projeto é de código aberto e distribuído sob a Licença MIT. Sinta-se à vontade para usá-lo, modificar e distribuir conforme necessário. Se você achar este projeto útil, agradecemos suas contribuições e feedback.

Se você tiver alguma dúvida ou encontrar problemas, por favor, não hesite em abrir um problema ou entrar em contato conosco.
