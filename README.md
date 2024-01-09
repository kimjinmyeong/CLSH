## CLSH
- A simple cluster shell for executing commands on multiple remote shells and collecting the results for output.
- 이 프로젝트에서 구현한 CLSH는 멀티 호스트 환경에서 SSH를 사용하여 원격으로 다수의 쉘을 연결하고, 명령어 수행 및 결과를 출력하는 기능을 수행한다.

## CLSH 설계 

이 프로젝트에서 구현한 CLSH는 멀티 호스트 환경에서 SSH를 사용하여 원격으로 다수의 쉘을 연결하고, 명령어 수행 및 결과를 출력하는 기능을 수행한다.

이 때 멀티 호스트 환경은 다음과 같은 구조이다.

![image](https://res.craft.do/user/full/4104a0ca-0aaa-3940-b8df-f87a564bc3ae/doc/5C511F06-BA79-463A-8DDB-2938275AE267/C47ACF2F-7585-48B7-BFC4-C97065C9B1BA_2/cn2GCOo7H8BY3tUOhd8rCl9DtOLYg8mbTEYxT9IJpT8z/Image.png)

Docker compose를 통해 하나의 Main node와 4개의 node들로 구성하였다.  
Main node에서 다른 node들과의 연결은 SSH를 사용하였고, PIPE를 사용하여 SSH로 연결한 프로세스와 node간에 통신을 하는 방식으로 구현하였다. PIPE는 stdin, stdout, stderr로 각 node별 3개의 PIPE를 구성하였다.   
또한 `sshpass` 를 사용하여 ssh 연결 시 비밀번호 입력이 없도록 하였다.

### 컴파일 및 설치 방법


#### 요구 사항

1. Python3 ([Install Link](https://www.python.org/downloads/))
2. Docker ([Install Link](https://docs.docker.com/get-docker/))

#### 설치 방법

1.   터미널에서 Dockerfile과 docker-compose.yml이 있는 디렉토리로 이동한다.
2.  `docker-compose up -d --build` 를 입력하여 Docker 컨테이너를 빌드하고 시작한다.

### 빠르게 시작하기

1. 설치한 docker 컨테이너를 시작한다.
2. `docker compose exec -it main /bin/bash`  
를 입력하여 `main` 컨테이너에 연결하고, `source` 디렉토리로 이동한다.
3. `python3 clsh.py -h node1,node2,node3,node4 cat /proc/loadavg` 를 입력하면 각 프로세스의 부하를 확인할 수 있는 정보를 출력한다.

#### 예시


![image](https://res.craft.do/user/full/4104a0ca-0aaa-3940-b8df-f87a564bc3ae/doc/5C511F06-BA79-463A-8DDB-2938275AE267/F771AC72-90D5-498A-9BF7-4C4048A5367E_2/dxU2RyMGIrk3ub3qBEteNC4h1o9sUmDWrT2tRHMCpOYz/Image.png)

기본적인 사용 방법은 `python3 clsh.py {option} {host} {command}`이다.

### 각 옵션 및 사용방법


- #### -h


`-h` 옵션은 사용자가 연결할 노드들을 입력하는 옵션이다. 복수의 node의 경우 ',' 로 구분해주어야 한다.  
사용방법은 `python3 clsh.py -h {node} {command}` 이다.

다음은 node1, node2, node3에 연결하여 pwd 명령어를 수행하고 결과를 출력한 예시이다.

![image](https://res.craft.do/user/full/4104a0ca-0aaa-3940-b8df-f87a564bc3ae/doc/5C511F06-BA79-463A-8DDB-2938275AE267/5C139BB6-E3AA-400E-9431-BFE9BF43E3E8_2/iMrBlQC5TCdpxxdt2QiJv528O9ezxi6uhhJIeWH6wC4z/Image.png)

- #### --hostfile


프로그램을 실행하는 디렉토리에 `hostfile` 데이터를 불러오는 옵션이다. `hostfile` 은 각 라인 별로 node의 host가 써있어야 한다.

옵션의 사용법은 `python3 clsh.py --hostfile {hostfile path} {command}`

다음은 예시 `hostfile`이다.

```shell
node1
node2
node3
node4
```


다음은 위 `hostfile`을 사용하여 --hostfile 옵션을 통해 `cat /proc/loadavg`명령어를 입력한 결과이다.

![image](https://res.craft.do/user/full/4104a0ca-0aaa-3940-b8df-f87a564bc3ae/doc/5C511F06-BA79-463A-8DDB-2938275AE267/4C81DCBE-68A7-4325-A783-96C34C6A0792_2/xe6ySjYjUEwMlIPhH8yOCyyeLKnQQof6dWeVsSwoxpwz/Image.png)

- #### Interactive 모드


#### `-i` 옵션을 사용하여 Interactive 모드 활성화


`python3 clsh.py -i` 를 입력하면 Interactive 모드 활성화가 가능하다.  
사용자는 연결 가능한 node들 중에서 1:1로 연결할 node를 입력한다.  
그 후 명령어를 입력하여 결과를 얻고, "quit” 또는 “exit” 입력을 통해 프로그램을 종료할 수 있다.  
단, host는 `CLSH_HOSTS`, `CLSH_HOSTFILE`, `hostfile`중에서 정보를 가져온다.

#### 예시


![image](https://res.craft.do/user/full/4104a0ca-0aaa-3940-b8df-f87a564bc3ae/doc/5C511F06-BA79-463A-8DDB-2938275AE267/E2850E8A-ABB3-4349-860C-0BB3246E3363_2/RNy70dNRzSrLy1szlJq6s0RaAycq7HW65yowE1F0aCMz/Image.png)

#### `-i` 옵션과 명령어를 입력하지 않고 Interactive 모드 활성화


`python3 clsh.py {option} {node}` 를 입력하여 모드를 활성화한다.  
사용자가 직접 host 또는 hostfile을 통해 연결하거나, 옵션 1 조건에 따라서 연결 가능한 node들을 모두 연결하고 명령어를 입력 및 결과를 출력한다.   
맨 앞에 ‘!'를 붙이면 현재 실행한 `LOCAL` 쉘에서 명령어를 실행하고 출력한다.

#### 예시


![image](https://res.craft.do/user/full/4104a0ca-0aaa-3940-b8df-f87a564bc3ae/doc/5C511F06-BA79-463A-8DDB-2938275AE267/79DB9F58-4929-4B8D-9A58-3D0F44976475_2/jJjQj5VXcUlUm10alxep2helL2y5uFT8APsyU6TyLbMz/Image.png)

![image](https://res.craft.do/user/full/4104a0ca-0aaa-3940-b8df-f87a564bc3ae/doc/5C511F06-BA79-463A-8DDB-2938275AE267/FDA68DE3-3698-4936-94FC-228396BBDC38_2/RGlaQpwYixU8AF1xBxM1HHV7xnu09JmvcwCB1Q8igT0z/Image.png)

## 이 프로그램의 한계


### 무한 대기 문제


interactive 모드에서 아무런 결과 값을 못 불러오는 경우, 프로그램이 계속해서 결과가 돌아오기를 기다려서 결국 진행할 수 없게된다. 이 문제는 `response = ssh_process.stdout.readline()` 에서 발생하는데, 이는 프로세스의 표준 출력에서 한 줄을 읽어오는 함수이며, 만약 표준 출력에 아무런 결과가 없으면 이 함수는 계속해서 결과가 올 때까지 기다리기 때문이다. 이러한 동작 때문에 결과가 도착하지 않는 한 해당 라인에서 프로그램이 Block되는 현상이 발생한다. 

프로그램을 비동기적으로 구현한다면 timeout 같은 조건을 걸어 해결이 가능할 것으로 예상한다.

#### 문제 재현


![image](https://res.craft.do/user/full/4104a0ca-0aaa-3940-b8df-f87a564bc3ae/doc/5C511F06-BA79-463A-8DDB-2938275AE267/BE95BDB7-8FDC-4D77-9FA8-91952D52F3E0_2/GpzyfANtC3XB15Ykrc86y3ruy87O4sPxPcSNRIx0C0Az/Image.png)

