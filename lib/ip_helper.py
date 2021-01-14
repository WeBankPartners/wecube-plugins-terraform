# cording=utf8
# author="rd"

import IPy


def check_ip(ip):
    if ip is None:
        return False, "ip is null"
    if not isinstance(ip, basestring):
        return False, "not ip"
    if ip.strip():
        if not len(ip.split("/")) == 1:
            return False, "%s is invalid ip address" % ip
        else:
            try:
                t_res = ip.split(".")
                if len(t_res) != 4:
                    return False, "not ip"
                IPy.IP(ip).strNormal()
                return True, "ok"
            except Exception, e:
                return False, e
    else:
        return False, "ip is null"


def check_cidr(cidr):
    if cidr is None:
        return False, "cidr is null"
    if not isinstance(cidr, basestring):
        raise False, "not cinder"
    if cidr.strip():
        if "/" not in cidr:
            return False, "not cidr"
        else:
            try:
                IPy.IP(cidr).strNormal()
                return True, "ok"
            except:
                return False, "not cidr"

    else:
        return False, "cidr is null"


def check_cidr(cidr, ip):
    try:
        return ip in IPy.IP(cidr)
    except:
        return False




if __name__ == '__main__':
    pass
# ips = ' ,'
# status, result = check_ips(ips)
# print status, result
