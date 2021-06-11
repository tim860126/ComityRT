# ComityRT

#### ComityRT是一個幫助系統設計人員創建混合關鍵性系統的測試化平台。

#### 使用組態檔的方式，快速建立部屬多個不同CPU、Memory、排程方法等等配置的混合關鍵性系統

#### 透過虛擬化技術Docker，我們將Container視為關鍵層級，隔離運行系統工作在其中

#### 提供可視化的介面顯示CPU使用率以及系統工作與關鍵層級佇列運行狀況
![Menu](/image/Menu.png)

![Scheduler](/image/Scheduler.png)


## 系統組態檔參數
ComityRT建置系統的組態檔參數設定說明

系統主要設定區塊`ComityRT`

| ComitRT                   | 系統參數 |
| --------------------------|:-------------:|
| num_Criticality_Level     | 關鍵層級數量,若要系統關鍵層級數量為三個則設置3 |
| Pirority_assignment_method| 預設優先權分配方法 |
| System_MaxNum_Cores_Limit | 是否限制系統使用CPU數量|
| System_Use_Cores          | 設置系統使用CPU編號|
| Workload_Name             | 工作設定檔名稱 |
| Execution_Level_Mode      | 系統初始運行關鍵層級 |
| Change_Level_Mode         | 是否允許工作搬移/切換運行的關鍵層級|
| Scheduleability_analysis  | 選用排程分析方法 |

系統關鍵層級區塊`任意名稱`ex: Level1、Level2

| 關鍵層級                  | 關鍵層參數 |
| --------------------------|:-------------:|
| Sub_Level                 | 允許子層級建立,若父層級有工作等待中將會進入子層級運作 |
| Level_Use_Cores           | 指定使用CPU編號,若要選擇第一個CPU為編號0,可以設置多CPU如0,1,3|
| Level_Cores_Weights       | 限制指定CPU使用率,若要使用整顆CPU的量則為1若要一半則為0.5|
| Level_Memory_Limit        | 限制層級Memory使用量,若要限制最多使用500MB 則填入500|
| Level_Priority_Mode       | 工作排程方法的選用如:RM,EDF,CFS|

子關鍵層級區塊與父關鍵層級參數設定一樣，但無`Sub_Level`與`Level_Priority_Mode`

## 系統組態檔範例

此範例會建立一個雙關鍵層級系統

Level1 配置1.5顆CPU使用量分別指定0與1的CPU編號

Level2 配置1.2顆CPU使用量分別指定1與2的CPU編號 

```
[ComityRT]
num_Criticality_Level = 2

Pirority_assignment_method =SMC

System_MaxNum_Cores_Limit = True

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

Level_Memory_Limit=3000

Level_Priority_Mode=EDF

        [[level_2]]
        Level_Use_Cores=2

        Level_Cores_Weights=0.7

        Level_Memory_Limit=300


```
