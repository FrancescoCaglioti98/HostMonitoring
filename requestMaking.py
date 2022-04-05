from socket import timeout
import requests
import psycopg2

hostname = 'localhost'
database = 'test'
username = 'postgres'
pwd = 'TestPostGre'
port_id = 5432
conn = None
cur = None

def getIP():
    ip_array = []
    try:
        conn = psycopg2.connect(
            host = hostname,
            dbname = database,
            user = username,
            password = pwd,
            port = port_id)
        cur = conn.cursor()

        cur.execute('SELECT IP from ips')
        
        for ip in cur.fetchall():
            new_ip = ip[0][0:-3]
            ip_array.append(new_ip)

        conn.commit()
    except Exception as error:
        print(error)

    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()
    
    return ip_array

def cpuUsage(IP):
    apiCall = '/cpu/percent?aggregate=avg&token=myToken'
    cpu = tryBlock(IP, apiCall)

    if cpu != -1:
        jason = cpu.json()
        percentage = jason['percent'][0]
        return percentage
    else:
        return [-1]
    
def cpuIdle(IP):
    apiCall = '/cpu/idle?aggregate=avg&token=myToken'
    idle = tryBlock(IP, apiCall)

    if idle != -1:
        jason = idle.json()
        idleTime = jason['idle'][0]
        return idleTime
    else:
        return [-1]

def diskLogical(IP):
    apiCall = '/disk/logical/C:|?units=G&token=myToken'

    disk = tryBlock(IP, apiCall)

    if disk != -1:
        jason = disk.json()

        used = jason['C:|']['used'][0]
        total = jason["C:|"]['total'][0]
        free = jason["C:|"]['free'][0]
        array = []
        array.append(used)
        array.append(total)
        array.append(free)

        return array
    else:
        return [-1,-1,-1]

def bytesRecived(IP):
    apiCall = '/interface/Wi-Fi/bytes_recv?units=G&token=myToken'
    recived = tryBlock(IP, apiCall)

    if recived != -1:
        jason = recived.json()
        bytes = jason['bytes_recv'][0]    
        return bytes

    else:
        return recived

def bytesSent(IP):
    apiCall = '/interface/Wi-Fi/bytes_sent?units=G&token=myToken'
    sent = tryBlock(IP, apiCall)

    if sent != -1:
        jason = sent.json()
        bytes = jason['bytes_sent'][0]
        return bytes
    else:
        return sent

def ramUsage(IP):
    apiCall = '/memory/swap?units=G&token=myToken'
    ram = tryBlock(IP, apiCall)

    if ram != -1:
        jason = ram.json()
        used = jason['swap']['used'][0]
        total = jason["swap"]['free'][0]
        free = jason["swap"]['total'][0]

        array = []
        array.append(used)
        array.append(total)
        array.append(free)
        return array
    else:
        return [-1,-1,-1]

def virtualUsage(IP):
    apiCall = '/memory/virtual?units=G&token=myToken'
    virtual = tryBlock(IP, apiCall)

    if virtual != -1:
        jason = virtual.json()
        used = jason['virtual']['used'][0]
        total = jason["virtual"]['free'][0]
        free = jason["virtual"]['total'][0]

        array = []
        array.append(used)
        array.append(total)
        array.append(free)
        return array
    else:
        return [-1,-1,-1]

def lanRecived(IP):
    apiCall = '/interface/Ethernet/bytes_recv?units=G&token=myToken'
    lan = tryBlock(IP, apiCall)
   


    if lan != -1:
        jason = lan.json()
        bytes = jason['bytes_recv'][0]
        return bytes
    else:
        return lan

def lanSent(IP):
    apiCall = '/interface/Ethernet/bytes_sent?units=G&token=myToken'
    lan = tryBlock(IP, apiCall)
    

    if lan != -1:
        jason = lan.json()
        bytes = jason['bytes_sent'][0]
        return bytes
    else:
        return lan

def tryBlock(IP, apiCall):
    try:
        call = requests.get('https://'+IP+':5693/api'+apiCall, verify=False, timeout= 1.0)
        if 'error' in call.json():
            call = -1

        return call
    
    except Exception as error:
        return -1

networkIP = getIP()

for singleIP in networkIP:
    cpu_percentage_usage = cpuUsage(singleIP)
    cpu_idle_time = cpuIdle(singleIP)
    logical_disk = diskLogical(singleIP)
    recived_byte = bytesRecived(singleIP)
    sent_byte = bytesSent(singleIP)
    ram = ramUsage(singleIP)
    virtual_usage = virtualUsage(singleIP)
    lan_recived = lanRecived(singleIP)
    lan_sent = lanSent(singleIP)


    values = []
    values.append(cpu_percentage_usage)
    values.append(cpu_idle_time)
    for value in logical_disk:
        values.append(value)
    values.append(lan_recived)
    values.append(lan_sent)
    values.append(recived_byte)
    values.append(sent_byte)
    for value in ram:
        values.append(value)
    for value in virtual_usage:
        values.append(value)
    
    try:
        conn = psycopg2.connect(
            host = hostname,
            dbname = database,
            user = username,
            password = pwd,
            port = port_id)
        cur = conn.cursor()

        insert_script = '''
        INSERT INTO checks (time_of_check, ip, cpu_percentage_usage, cpu_idle, disk_used, disk_free, disk_total, lan_recived, lan_sent, wifi_recived, wifi_sent, ram_used, ram_free, ram_total, ram_virtual_used, ram_virtual_free, ram_virtual_total)
        VALUES (CURRENT_TIMESTAMP, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''

        insert_value = (singleIP, values[0][0], values[1][0], values[2], values[4], values[3], values[5], values[6], values[7], values[8], values[9], values[10], values[11], values[12], values[13], values[14])

        cur.execute(insert_script, insert_value)

        conn.commit()
    except Exception as error:
        print(error)

    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()
