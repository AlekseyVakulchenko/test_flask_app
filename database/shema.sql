create type object_type as enum ('apartment', 'apartments', 'penthouse');
create table station
(
    station_id   int primary key not null,
    station_name varchar(255) not null
);

create table real_estate_object
(
    real_estate_object_id   int primary key not null,
    real_estate_object_name varchar(255) not null,
    address                 varchar(50) not null,
    floor                   smallserial not null,
    object_type             object_type not null,
    square                  smallserial not null
);

create table real_estate_object_station
(
    object_station_id     int primary key not null,
    station_id            int REFERENCES station (station_id)  ON UPDATE CASCADE,
    real_estate_object_id int REFERENCES real_estate_object (real_estate_object_id) ON UPDATE CASCADE ON DELETE CASCADE
);
