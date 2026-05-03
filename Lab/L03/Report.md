<!--
任务一

1. 建立简单拓扑图；
(a)

一台服务器 
一台 2960 交换机 
一台 1841 路由器 
一台集线器 
一部 IP 电话 
一台 PC 
使用自动连接方式连接设备
70F5868B7577864DD78EF93979D65C8C.jpg

(b)

编辑

数据库服务器

网络信息中心

网管工作站

Web服务器

光缆

双绞线

防火墙

光缆

路由器

万兆
交换机

光缆

双绞线

光缆

光缆

光缆

双绞线

千兆
交换机

百兆
交换机

E1552D13CD374FD0E11FAAB9DD36A2F6.jpg

任务二

1. 利用一台型号为2960的交换机将2台pc机互联组件一个小型局域网；
2. 分别设置pc机的IP地址；
3. 验证pc机间可以互通。

817A27A1409B55E5ED56F864AF92A5A6.jpg

任务三

1.  利用一台路由器，两台交换机和3台pc、1台笔记本，建立一个网络；
2. 分别设置pc机的IP地址；
3.验证pc机间可以互通。

6AAD72CDB6205753BE49E68DB75E434A.png
-->
# Report 3
## 1. Experiment Name
Network Topology Design and Configuration

## 2. Experiment Tasks
### Task 1
#### (a)
Establish a simple topology diagram:
- A server
- A 2960 switch
- A 1841 router
- A hub
- An IP phone
- A PC
Use automatic connection to connect the devices.
![T1_a](../Assets/img/70F5868B7577864DD78EF93979D65C8C.jpg)

#### (b)
Edit
![T1_b](../Assets/img/E1552D13CD374FD0E11FAAB9DD36A2F6.jpg)

### Task 2
1. Use a 2960 switch to interconnect two PCs to form a small local area
2. Set the IP addresses of the PCs respectively
3. Verify that the PCs can communicate with each other

![T2](../Assets/img/817A27A1409B55E5ED56F864AF92A5A6.jpg)

### Task 3
1. Use a router, two switches, three PCs, and one laptop to establish a network
2. Set the IP addresses of the PCs respectively
3. Verify that the PCs can communicate with each other

![T3](../Assets/img/6AAD72CDB6205753BE49E68DB75E434A.png)

## 3. Experiment Environment and Tools
- M4 MacBook Air
- Cisco Packet Tracer (Version 9.0.0.0810)

## 4. Experiment Records and Result Analysis
### 4.1 Records
#### Task 1
##### (a)
![](../Assets/img/29C58F44FD13C367C6CD333FEE2DCA43.png)

To power on the IP phone, click the IP phone, go to     `Physical` tab, and click and drag the `IP_PHONE_POWER_ADAPTER` from the right panel to the IP phone's power port.
![](../Assets/img/A83A69E0A23D27FACEC1A8FD832BD8D9.png)

##### (b)
![](../Assets/img/9A870226DF14503FC4495CF8E795C334.png)

#### Task 2
![](../Assets/img/61D70BBD18BAAD43EC7C684C2C4B394B.png)

Click PC0, go to `Config` tab, go to `FastEthernet0`, set the IP address to 192.168.1.1 and subnet mask is automatically set to 255.255.255.0.
![](../Assets/img/8203412A4148F8093C3F5F473CDFC004.png)

Then the same for PC1, but set the IP address to 192.168.1.2.
![](../Assets/img/F1FB5E247910A95FAB5E43DC628CDBC3.png)

Then click PC0, go to `Desktop` tab, click on `Command Prompt`, and type `ping 192.168.1.1` to ping itself, and it is successful. Then type `ping 192.168.1.2` to ping PC1, and it is successful.
![](../Assets/img/6249B06857BE18052339563F3F34F67C.png)

The same for PC1, ping itself and ping PC0, both are successful.
![](../Assets/img/70E8B7E57944106C52E7388245F166D1.png)

#### Task 3
![](../Assets/img/3A78ACAB8EB72F40103CA040C3BC6748.png)

To start and configure the router, click the router, go to `CLI` tab, and enter the following commands
```bash
enable
configure terminal
interface fa0/0
ip address 192.168.1.1 255.255.255.0
no shutdown
exit
interface fa0/1
ip address 192.168.2.1 255.255.255.0
no shutdown
exit
end
```
![](../Assets/img/9CDBEE20CB4F77DE53D1E0C132A04329.png)

Then configure the PCs. Set PC0's and PC1's default gateway to 192.168.1.1 and their IP addresses to 192.168.1.2 and 192.168.1.2 respectively. Set PC2 and Laptop0's default gateway to 192.168.2.1 and their IP addresses to 192.168.2.2 and 192.168.2.3 respectively.
![](../Assets/img/7569C735FA6478C9FACB58790ED25130.png)
![](../Assets/img/9ECBA93458DAD8B26958CD11B335F3FA.png)

Then ping between the router, PCs and laptop to verify they can communicate with each other. First ping from PC0 to PC2, and it is successful.
![](../Assets/img/C03653A872B2D5379FB66D2E38BCAC5C.png)
![](../Assets/img/F10B332B369670BC4251B8A71D33E763.png)

### 4.2 Analysis
#### Task 1
##### (a)
None.

##### (b)
None.

#### Task 2
None.

#### Task 3
None.

## 5. Problems Encountered and Solutions
### 5.1 Problems
#### Task 1
##### (a)
None.

##### (b)
1. Can't follow the cable types in the figure (fiber can't connect to the Serve).

#### Task 2
None.

#### Task 3
None.

### 5.2 Solutions
#### Task 1
##### (a)
None.

##### (b)
1. Use "Automatic Choose Connection Type" to connect the devices, and it will automatically choose the correct cable type.

#### Task 2
None.

#### Task 3
None.
