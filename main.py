import multiprocessing
import subprocess
from mac_vendor_lookup import MacLookup
import datetime

class lista_ips:
    def __init__(self, lista_ips):
        self.lista_ips = lista_ips
class Ip_conectado:
    def __init__(self, ip, mac, fabricante, primeira_descoberta, ultima_descoberta):
        self.ip = ip
        self.mac = mac
        self.fabricante = fabricante
        self.primeira_descoberta = primeira_descoberta
        self.ultima_descoberta = ultima_descoberta
        self.nr_conexoes = 1

def my_own_mac():
    ret = subprocess.check_output('ipconfig /all', universal_newlines=True)
    for line in ret.splitlines():
        if(line[:9] == "   Endere"):
            mac = line.strip()
            break
    for letter in mac:
        if (letter.isnumeric() == False):
           mac = mac.replace(letter, "", 1)
        else:
            break
    return mac

def others_mac(ret, ip):
    tamanho_ip = len(ip)
    for mac in ret.splitlines():
        #print(line[:tamanho_ip + 2])
        if(mac[:tamanho_ip + 2] == "  " + ip):
            mac = mac.replace(ip,"", 1).strip()
            mac = mac[:17]
            return mac


def search_mac(ip):
    ret = subprocess.check_output(['arp', '-a' ,ip], universal_newlines=True)
    if(ret.find('foi encontrada') != -1):
        mac = my_own_mac()
    else:
        mac = others_mac(ret, ip)
    return mac

def pinging(ip, ips_validos):
    try:
        ret = subprocess.check_output(['ping',ip ,'-n','1'], universal_newlines=True)
        if(ret.find('TTL') != -1):
            # print("IP: " + ip + " localizado com sucesso!")
            if(ip not in ips_validos):
                ips_validos.append(ip)
    except:
        pass
def get_gateway():
    gateway = subprocess.check_output('ipconfig', universal_newlines=True)
    
    for line in gateway.splitlines():
        if(line[:4] == "   G"):
            gateway = line.strip()
            break

    for letter in gateway:
        if (letter.isnumeric() == False):
            gateway = gateway.replace(letter, "", 1)
        else:
            break
        
    return gateway

def get_ips(ip_teste, ips):
    for ip_testado in range(1,255):
        ips.append((ip_teste[:-1] + str(ip_testado)))
    return ips

if __name__ == '__main__':
    lista_conn = []
    threads = []
    mac_lk = MacLookup()
    mac_lk.update_vendors()

    while(True):
        ips = []
        ips_validos = multiprocessing.Manager().list()
        macs = []
        fabricantes = []

        #PEGANDO O IP PADRÃO
        gateway = get_gateway()
        ip_teste = gateway
        
        #GERANDO A LISTA DE IPS POSSÍVEIS
        ips = get_ips(ip_teste, ips)
        
        #CRIANDO OS PROCESSOS PARA PROCURAR OS IPS
        processes = [multiprocessing.Process(target=pinging, args=(ip, ips_validos)) for ip in ips]
        for process in processes:
            process.start()
        
        for process in processes:
            process.join()

        for ip in ips_validos:
            macs.append(search_mac(ip))

        

        for mac in macs:
            fabricantes.append(mac_lk.lookup(mac))


        achou_igual = False
        for i in range(len(ips_validos)):
            for ip_conectado in lista_conn:
                if(ips_validos[i] == ip_conectado.ip):
                    achou_igual = True
                    ip_conectado.ultima_descoberta = str(datetime.datetime.now())
                    ip_conectado.nr_conexoes = ip_conectado.nr_conexoes + 1
            if(achou_igual == False):
                conexao = Ip_conectado(ips_validos[i], macs[i], fabricantes[i], str(datetime.datetime.now()), str(datetime.datetime.now()))
                lista_conn.append(conexao)
            achou_igual = False

        for conexao in lista_conn:
            print('IP: ' + conexao.ip)
            print('MAC: ' + conexao.mac)
            print('FAB: ' + conexao.fabricante)
            print('FIRST: ' + conexao.primeira_descoberta)
            print('LAST: ' + conexao.ultima_descoberta)
            print('COUNT: ' + str(conexao.nr_conexoes))
            print("")

    