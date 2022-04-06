from datetime import datetime
from socket import timeout
import requests
import psycopg2
import time
from configparser import ConfigParser

conn = None
cur = None

def get_ip():
    try:
        FILE = 'config.ini'
        CONFIG = ConfigParser()
        CONFIG.read(FILE)
        
        conn = psycopg2.connect(
            host = CONFIG['database']['hostname'],
            dbname = CONFIG['database']['database'],
            user = CONFIG['database']['username'],
            password = CONFIG['database']['pwd'],
            port = CONFIG['database']['port_id'])
        cur = conn.cursor()

        cur.execute('SELECT IP from ips')
        ip_array = []
        
        for ip in cur.fetchall():
            new_ip = ip[0][0:-3]
            ip_array.append(new_ip)

        conn.commit()
    except Exception as error:
        file = open(r"Path to a TXT LOG FILE", "a")
        string = 'The error occured at ' + str(datetime.now())+ ' is relative to: '+str(error) + '\n\n'
        file.write(string)
        file.close()

    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()
    
    return ip_array

def cpu_usage(IP):
    api_call = '/cpu/percent?aggregate=avg&token=myToken'
    cpu = try_block(IP, api_call)

    if cpu != -1:
        jason = cpu.json()
        percentage = jason['percent'][0]
        return percentage
    else:
        return [-1]
    
def cpu_idle(IP):
    api_call = '/cpu/idle?aggregate=avg&token=myToken'
    idle = try_block(IP, api_call)

    if idle != -1:
        jason = idle.json()
        idleTime = jason['idle'][0]
        return idleTime
    else:
        return [-1]

def disk_logical(IP):
    api_call = '/disk/logical/C:|?units=G&token=myToken'

    disk = try_block(IP, api_call)

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

def bytes_recived(IP):
    api_call = '/interface/Wi-Fi/bytes_recv?units=G&token=myToken'
    recived = try_block(IP, api_call)

    if recived != -1:
        jason = recived.json()
        bytes = jason['bytes_recv'][0]    
        return bytes

    else:
        return recived

def bytes_sent(IP):
    api_call = '/interface/Wi-Fi/bytes_sent?units=G&token=myToken'
    sent = try_block(IP, api_call)

    if sent != -1:
        jason = sent.json()
        bytes = jason['bytes_sent'][0]
        return bytes
    else:
        return sent

def ram_usage(IP):
    api_call = '/memory/swap?units=G&token=myToken'
    ram = try_block(IP, api_call)

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

def virtual_usage(IP):
    api_call = '/memory/virtual?units=G&token=myToken'
    virtual = try_block(IP, api_call)

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

def lan_recived(IP):
    api_call = '/interface/Ethernet/bytes_recv?units=G&token=myToken'
    lan = try_block(IP, api_call)
   


    if lan != -1:
        jason = lan.json()
        bytes = jason['bytes_recv'][0]
        return bytes
    else:
        return lan

def lan_sent(IP):
    api_call = '/interface/Ethernet/bytes_sent?units=G&token=myToken'
    lan = try_block(IP, api_call)
    

    if lan != -1:
        jason = lan.json()
        bytes = jason['bytes_sent'][0]
        return bytes
    else:
        return lan

def try_block(IP, apiCall):
    try:
        call = requests.get('https://'+IP+':5693/api'+apiCall, verify=False, timeout= 1.0)
        if 'error' in call.json():
            call = -1

        return call
    
    except Exception as error:
        print(error)
        return -1



while True:
    ip_array = get_ip()

    for singleIP in ip_array:
        values = []
        values.append(cpu_usage(singleIP))
        values.append(cpu_idle(singleIP))

        logical_disk = disk_logical(singleIP)
        for value in logical_disk:
            values.append(value)
        
        values.append(lan_recived(singleIP))
        values.append(lan_sent(singleIP))
        values.append(bytes_recived(singleIP))
        values.append(bytes_sent(singleIP))
        ram = ram_usage(singleIP)
        for value in ram:
            values.append(value)
        virtual_ram = virtual_usage(singleIP)
        for value in virtual_ram:
            values.append(value)
        
        try:
            FILE = 'config.ini'
            CONFIG = ConfigParser()
            CONFIG.read(FILE)

            conn = psycopg2.connect(
                host = CONFIG['database']['hostname'],
                dbname = CONFIG['database']['database'],
                user = CONFIG['database']['username'],
                password = CONFIG['database']['pwd'],
                port = CONFIG['database']['port_id'])
            cur = conn.cursor()

            insert_script = '''
            INSERT INTO checks (time_of_check, ip, cpu_percentage_usage, cpu_idle, disk_used, disk_free, disk_total, lan_recived, lan_sent, wifi_recived, wifi_sent, ram_used, ram_free, ram_total, ram_virtual_used, ram_virtual_free, ram_virtual_total)
            VALUES (CURRENT_TIMESTAMP, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''

            insert_value = (singleIP, values[0][0], values[1][0], values[2], values[4], values[3], values[5], values[6], values[7], values[8], values[9], values[10], values[11], values[12], values[13], values[14])

            cur.execute(insert_script, insert_value)

            conn.commit()
        except Exception as error:
            file = open(r"Path to a TXT LOG FILE", "a")
            string = 'The error occured at ' + str(datetime.now())+ ' is relative to: '+str(error) + '\n\n'
            file.write(string)
            file.close()
            print(error)

        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                conn.close()

    time.sleep(60)