# ComityRT

ComityRT是一個幫助系統設計人員創建混合關鍵性系統的測試化平台。

使用組態檔的方式，快速建立部屬多個不同CPU、Memory、排程方法等等配置的混合關鍵性系統

透過虛擬化技術Docker，我們將Container視為關鍵層級，隔離運行系統工作在其中

提供可視化的介面顯示CPU使用率以及系統工作與關鍵層級佇列運行狀況
 
<div align=center>
<img src="/image/Menu.png" alt="Menu" width="75%"/>
<img src="/image/Scheduler.png" alt="Scheduler" width="75%"/>
</div>


## 系統組態檔參數
ComityRT建置系統的組態檔參數設定說明

* Preemption 工作搶占

  ComityRT建置系統環境時，依據組態檔的系統參數`System_Preemption`判斷系統是否允許工作根據優先權的高低進行執行的搶占

* Change_Level_Mode 工作關鍵層級搬移

  我們將容器視為關鍵層級，為了要實現工作關鍵層級的切換或是將工作搬移到其他CPU上等情況(Level1關鍵層級配置了0號CPU、Level2配置了1號CPU，當某一個工作要轉移到1號CPU上運作時，就會透過此模組進行工作的搬移)
  
  因應此需求我們實作出一個Change_Level_Mode模組，將容器內正在運作中的工作進行搬移到指定的關鍵層級(也就是此關鍵層級的容器中)
  
  根據[Docker Document](https://docs.docker.com/config/containers/runmetrics/) 
  
  說明Docker創建容器時會在`/sys/fs/cgroup/memory/system.slice/docker-<longid>.scope/ on cgroup v1, systemd driver`建立相對應的cgroup
  
  因此可以透過下列語法容器的名稱查找容器的ID
  
  ```
  docker inspect -f '{{.ID}}' [container_name]
  ```
  
  並將工作PID寫入到對應的容器ID的cgroup所有層級內的Task就完成了容器內的工作搬移
  
* Sub_Level 子關鍵層級  

  與父關鍵層級的關鍵層級一致，主要目的在於分擔父關鍵層級的工作負載量，同時實現關鍵層級能夠配置不同CPU的使用率(Level1 配置了0與1編號的 CPU 50% 與 75%使用率)。
  
  由於Docker只能設定Container單顆CPU或是多顆的整體使用率，無法在多顆時單獨設定每顆的使用率(CPU0:50%、CPU1:25%)，因此在ComityRT中同一個關鍵層級可能會有一個或是多個容器運作。
  
  當父關鍵層級的主容器有工作運行且佇列中仍有工作在等待，且`Sub_Level=true`並有建立子關鍵層級,排程器會先確認子關鍵層級容器中沒有工作正在運行後，將佇列中最高優先權的工作搬移到子關鍵層級容器中運行。  
  
系統主要設定區塊`ComityRT`

| ComitRT                   | 描述 |
| --------------------------|-------------|
| num_Criticality_Level     | 關鍵層級數量,若要系統關鍵層級數量為三個則設置3 |
| Pirority_assignment_method| 預設優先權分配方法 |
| System_MaxNum_Cores_Limit | 是否限制系統使用CPU數量|
| System_Preemption			| 允許工作根據優先權進行搶占|
| System_Use_Cores          | 設置系統使用CPU編號|
| Workload_Name             | 工作設定檔名稱 |
| Execution_Level_Mode      | 系統初始運行關鍵層級 |
| Change_Level_Mode         | 是否允許工作搬移/切換運行的關鍵層級|
| Scheduleability_analysis  | 選用排程分析方法 |

系統關鍵層級區塊`任意名稱`ex: Level1、Level2

| 關鍵層級                  | 描述 |
| --------------------------|-------------|
| Sub_Level                 | 允許子層級建立,若父層級有工作等待中將會進入子層級運作 |
| Level_Use_Cores           | 指定使用CPU編號,若要選擇第一個CPU為編號0,可以設置多CPU如0,1,3|
| Level_Cores_Weights       | 限制指定CPU使用率,若要使用整顆CPU的量則為1若要一半則為0.5|
| Level_Memory_Limit        | 限制層級Memory使用量(以MB為單位),若要限制最多使用500MB 則填入500|
| Level_Priority_Mode       | 工作排程方法的選用如:RM,EDF,CFS|

子關鍵層級區塊與父關鍵層級參數設定一樣，但無`Sub_Level`與`Level_Priority_Mode`

## 系統組態檔範例

```
vim ./config/ComitRT.ini 建立系統組態檔

python ComitRT_Menu.py 執行ComityRT選單 選擇 Bulid System through configuration 建置系統環境

```

此範例會建立一個雙關鍵層級可搶占式系統

Level1 配置1.5顆CPU使用量分別指定0與1的CPU編號以及500MB記憶體使用量限制，運行的工作會依照RM排程方法分配優先權

Level2 配置1.2顆CPU使用量分別指定1與2的CPU編號以及300MB記憶體使用量限制，運行的工作會依照EDF排程方法分配優先權

```
[ComityRT]
num_Criticality_Level = 2

Pirority_assignment_method =SMC

System_MaxNum_Cores_Limit = true

System_Preemption = true

System_Use_Cores=0,1,2,3

Workload_Name=workload

Execution_Level_Mode=level1

Change_Level_Mode=false

Scheduleability_analysis=RM

[level1]
Sub_Level=true

Level_Use_Cores=0

Level_Cores_Weights=1

Level_Memory_Limit=500

Level_Priority_Mode=RM

        [[level1_1]]
        Level_Use_Cores=1

        Level_Cores_Weights=0.5

        Level_Memory_Limit=300

[level2]
Sub_Level=true

Level_Use_Cores=1

Level_Cores_Weights=0.5

Level_Memory_Limit=300

Level_Priority_Mode=EDF

        [[level_2]]
        Level_Use_Cores=2

        Level_Cores_Weights=0.7

        Level_Memory_Limit=300


```
## 系統工作檔說明

```
[work1]      <-工作名稱需與工作執行檔名稱相同
level=level1 <- 運行的關鍵層級
c=15		 <- 工作WCET執行時間
d=20		 <- 工作截限時間
t=50		 <-	工作週期
#非必要參數
[關鍵層級名稱]=[時間]
level2=15    <-此為工作搬移參數，當工作到達15秒後此工作將會搬移到關鍵層級level2並與依照level2的排程方法與其他工作分配優先權
```
工作檔範例
```
[work1]
level=level1
c=15
d=20
t=50

[work2]
level=level1
c=15
d=30
t=70
level2=5

[work3]
level=level2
c=20
d=50
t=70

```

