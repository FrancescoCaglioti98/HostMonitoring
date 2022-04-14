from datetime import datetime
from socket import timeout
import requests
import psycopg2
import time
from configparser import ConfigParser
import export as ef

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
            ip_array.append(ip[0][0:-3])

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
    
def cpu_user(IP):
    api_call = '/cpu/user?aggregate=avg&delta=true&token=myToken'
    user = try_block(IP, api_call)

    if user != -1:
        jason = user.json()
        userTime = jason['user'][0]
        return userTime
    else:
        return [-1]

def cpu_idle(IP):
    api_call = '/cpu/idle?aggregate=avg&delta=true&token=myToken'
    idle = try_block(IP, api_call)

    if idle != -1:
        jason = idle.json()
        idleTime = jason['idle'][0]
        return idleTime
    else:
        return [-1]

def cpu_system(IP):
    api_call = '/cpu/system?aggregate=avg&delta=true&token=myToken'
    system = try_block(IP, api_call)

    if system != -1:
        jason = system.json()
        systemTime = jason['system'][0]
        return systemTime
    else:
        return [-1]

def disk_logical(IP):
    api_call = '/disk/logical/C:|?units=G&token=myToken'

    disk = try_block(IP, api_call)

    if disk != -1:
        jason = disk.json()

        array = []
        array.append(jason['C:|']['used'][0])
        array.append(jason["C:|"]['total'][0])
        array.append(jason["C:|"]['free'][0])

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

        array = []
        array.append(jason['swap']['used'][0])
        array.append(jason["swap"]['free'][0])
        array.append(jason["swap"]['total'][0])
        return array
    else:
        return [-1,-1,-1]

def virtual_usage(IP):
    api_call = '/memory/virtual?units=G&token=myToken'
    virtual = try_block(IP, api_call)

    if virtual != -1:
        jason = virtual.json()
        array = []
        array.append(jason['virtual']['used'][0])
        array.append(jason["virtual"]['free'][0])
        array.append(jason["virtual"]['total'][0])
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


#EXPORT OF TABLES EVERY DAY AT 22
    hour = datetime.now()
    controller_for_single_export = True

    if hour.hour == 22 and controller_for_single_export == True:
        for single_ip in ip_array:
            ef.checks_export(single_ip)

        controller_for_single_export = False


    if hour.hour == 23:
        controller_for_single_export = True



    for single_ip in ip_array:
        values = []
        values.append(cpu_usage(single_ip))
        values.append(cpu_idle(single_ip))

        logical_disk = disk_logical(single_ip)
        for value in logical_disk:
            values.append(value)
        
        values.append(lan_recived(single_ip))
        values.append(lan_sent(single_ip))
        values.append(bytes_recived(single_ip))
        values.append(bytes_sent(single_ip))
        ram = ram_usage(single_ip)
        for value in ram:
            values.append(value)
        virtual_ram = virtual_usage(single_ip)
        for value in virtual_ram:
            values.append(value)

        
        values.append(cpu_user(single_ip))
        values.append(cpu_system(single_ip))
        
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
            INSERT INTO checks (time_of_check, ip, cpu_percentage_usage, cpu_idle, disk_used, disk_free, disk_total, lan_recived, lan_sent, wifi_recived, wifi_sent, ram_used, ram_free, ram_total, ram_virtual_used, ram_virtual_free, ram_virtual_total, cpu_system_usage, cpu_user_usage)
            VALUES (CURRENT_TIMESTAMP, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''

            insert_value = (single_ip, values[0][0], values[1][0], values[2], values[4], values[3], values[5], values[6], values[7], values[8], values[9], values[10], values[11], values[12], values[13], values[14], values[16][0], values[15][0])

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