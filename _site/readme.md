

# Hướng dẫn cách import map từ openstreetmap vào SUMO simulation và tương tác điều chỉnh luồng giao thông thủ công 


## Xây dựng SUMO traffic với luồng giao thông random

Bước 1: Lên openstreepmat, chọn 1 area bản đồ bất kỳ và xuất ra file có đuôi .osm

Bước 2: chuyển osm  map sang SUMO 
network

VD: netconvert --osm-files map.osm -o test.net.xml

Bước 3 (tùy chọn): tạo route file. Nếu muốn sinh route theo ý thích thì bỏ qua bước này

Dùng file script randomTrips.py (có trong thư mục cài đặt của SUMO)

VD: python /home/tdinh/Documents/Project/sumo/tools/randomTrips.py -n danang.net.xml -r danang.rou.xml 

Bước 4: tạo file SUMO configuration (.sumocfg)

Mẫu:
```angular2html
<?xml version="1.0" encoding="UTF-8"?>

<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/sumoConfiguration.xsd">

    <input>
        <net-file value="danang.net.xml"/>
        <route-files value="danang.rou.xml"/>
    </input>

    <time>
        <begin value="0"/>
    </time>

    <report>
        <verbose value="true"/>
        <no-step-log value="true"/>
    </report>

</configuration>

```



Nhớ thay đổi tên <net-file> và <route-file> cho đúng với các file output của 2 bước trên


## Xây dựng SUMO traffic với luồng giao thông thiết lập thủ công (OD matrix)

Bước 0: chuẩn bị file .net.xml (tương ứng với bước số 2 ở trên)

Bước 1: Viết một file TAZ (Traffic Analysis zone) (name_file.taz.xml) theo mẫu 

```angular2html
<?xml version="1.0" encoding="UTF-8"?>

<additional xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/additional_file.xsd">

<tazs>
    <taz id="1" edges="583369723#0"></taz>
    <taz id="2" edges="656632915#5"></taz>
    <taz id="3" edges="656632914#5"></taz>
    <taz id="4" edges="583369723#4"></taz>
    <taz id="5" edges="656632915#0"></taz>
    <taz id="6" edges="767530315#4"></taz>

</tazs>

</additional>
```

trong đó các thẻ <taz> có các thuộc tính: 

* id: số bất kỳ
* edges: tập hợp các edge (các đường) được mô phỏng. Để có được số này, bạn phải mở file .net.xml ở trên trong SUMO, tại mỗi cạnh đường, copy edge name to clipboard và dán vào

Bản chất của bước này là định vị các con đường ta muốn tác động luồng giao thông. VD ở trên: ta đang có 6 lane sẽ tác động


Bước 3: Viết file OD (Origine-Destination) Matrix file (name_file.od) theo mẫu 

```angular2html
$O;D2
* From-Time  To-Time
0.00 1.00
* Factor
1.00
* some
* additional
* comments
         1          2       200
         1          3       200
         1          4       200
         1          6       200
         5          2       200
         5          3       200
         5          4       200
         5          6       200

```

ta quan tâm mỗi phần comment: 

VD 1 2 200 có nghĩa: có 200 xe đi từ edge có id 1 đen đến edge có id 2 (được định nghĩa ở bước 3)


Bước 4: Tạo 1 file config chứa thông tin ra file ở bước 2 và bước 3 (name_file.config.xml) theo mẫu


```angular2html
<?xml version="1.0" encoding="UTF-8"?>

<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/sumoConfiguration.xsd">

    <input>
        <taz-files value="taz_file.taz.xml"/>
        <od-matrix-files value="OD_file.od"/>
    </input>

</configuration>
```

Chú ý <taz-file> và <od-matrix-files> điền tên cho chính xác


Bước 5: Sinh file od_file.odtrips.xml thông qua lệnh od2trips

Lệnh: 

```
od2trips -c od2trips.config.xml -n taz_file.taz.xml -d OD_file.od -o od_file.odtrips.xml
```

chú ý od2trips sử dụng 3 file ở trên. Output file là od_file.odtrips.xml

Bước 6: Tạo file duarcfg_file (name_file.trips2routes.duarcfg) theo mẫu 

```angular2html
<?xml version="1.0" encoding="UTF-8"?>

<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/sumoConfiguration.xsd">

    <input>
        <net-file value="danang.net.xml"/>
        <route-files value="od_file.odtrips.xml"/>
    </input>

     <output>
        <output-file value="od_route_file.odtrips.rou.xml"/>
    </output>

    <report>
        <xml-validation value="never"/>
        <no-step-log value="true"/>
    </report>

</configuration>
```

File này sử dụng 2 file nhỏ: net-file và route-file sinh ra từ bước 6

Sau đó chạy lệnh sau, sẽ ra route file (name_file.rou.xml) (chú ý: tên của output file cũng được định nghĩa trong thẻ <output-file>)

```console
duarouter -c duarcfg_file.trips2routes.duarcfg
```

Bước 7: Tạo file config (.sumocfg)

```angular2html
<?xml version="1.0" encoding="UTF-8"?>

<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/sumoConfiguration.xsd">

    <input>
        <net-file value="danang.net.xml"/>
        <route-files value="od_route_file.odtrips.rou.xml"/>
    </input>

    <time>
        <begin value="0"/>
    </time>

    <report>
        <verbose value="true"/>
        <no-step-log value="true"/>
    </report>

</configuration>
```

Trong đó <route-files> sẽ là output file của bước 6




