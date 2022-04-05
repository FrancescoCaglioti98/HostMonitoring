CREATE TABLE ips(
    ip cidr NOT NULL PRIMARY KEY,
    business_unit VARCHAR(100) NOT NULL,
    host_name VARCHAR(100) NOT NULL
);

INSERT INTO ips( ip , business_unit, host_name) VALUES('HostIP', 'Meeting Room', 'Meeting Room 01');
INSERT INTO ips( ip , business_unit, host_name) VALUES('HostIP', 'Help Desk', 'HelpDesk 002');
INSERT INTO ips( ip , business_unit, host_name) VALUES('HostIP', 'Front Desk', 'Security 01');

CREATE TABLE checks(
    time_of_check TIMESTAMP PRIMARY KEY,
    IP cidr REFERENCES ips(ip),
    cpu_percentage_usage SMALLINT,
    cpu_idle INTEGER,
    disk_used FLOAT,
    disk_free FLOAT,
    disk_total FLOAT,
    lan_recived FLOAT,
    lan_sent FLOAT,
    wifi_recived FLOAT,
    wifi_sent FLOAT,
    ram_used FLOAT,
    ram_free FLOAT,
    ram_total FLOAT,
    ram_virtual_used FLOAT,
    ram_virtual_free FLOAT,
    ram_virtual_total FLOAT
);