<!--
任务
采用TCP协议实现一个简易的POP3客户端。支持功能：
1. 具有基本的登录和验证的功能，注意输入口令要以*号屏蔽。
2. 登录后能查看邮件列表，读取某邮件内容，删除某邮件内容

DNS的操作——gethostbyname ()
功能：查找主机名返回IP地址。
语法：# include <netdb.h>
　　　struct hostent *gethostbyname (const char *hostname);
返回值：成功时返回非空指针，失败时返回NULL。
说明：hostent结构的说明如下：
　　　struct hostent{
　　　　char	*h_name;	//主机的正式（规范）名字
　　　　char	**h_aliases;	//指向别名指针队列的指针
　　　　int	h_addrtype;	//AF_INET或AF_INET6
　　　　int	h_length;	//地址长度：4或16
　　　　char	**h_addr_list;	//指向地址指针链的指针					//地址均为网络字节顺序
　　　}
    错误发生时本函数并不设置errno，而设置h_errno变量。用hstrerror (h_errno)可取得错误的ascii描述。

4038E24D1A5878051A7782454FFDEDCF

3446E4F2C87F28C8A92C337638C69357

其他相关知识回顾
POP3一般端口号为110
POP3主要命令有：
USER username 认证用户名
PASS password 认证密码认证，认证通过则状态转换
STAT 处理请求 server 回送邮箱统计资料，如邮件数、 邮件总字节数
LIST n 处理 server 返回指定邮件的大小等
RETR n 处理 server 返回邮件的全部文本
DELE n 处理 server 标记删除，QUIT 命令执行时才真正删除
RSET 处理撤消所有的 DELE 命令
TOP n,m 处理返回 n 号邮件的前 m 行内容，m 必须是自然数
QUIT 希望结束会话。如果 server 处于"处理" 状态，则现在进入"更新"状态，删除那些标记成删除的邮件。如果 server 处于"认可"状态，则结束会话时 server 不进入"更新"状态 。
-->
# Report 7
## 1. Experiment Name

## 2. Experiment Tasks

## 3. Experiment Environment and Tools
- M4 MacBook Air

## 4. Experiment Records and Result Analysis
### 4.1 Records

### 4.2 Analysis

## 5. Problems Encountered and Solutions
### 5.1 Problems

### 5.2 Solutions
