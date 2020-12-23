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


def check_cider(cider):
    if cider is None:
        return False, "cider is null"
    if not isinstance(cider, basestring):
        raise False, "not cinder"
    if cider.strip():
        if "/" not in cider:
            return False, "not cider"
        else:
            try:
                IPy.IP(cider).strNormal()
                return True, "ok"
            except:
                return False, "not cider"

    else:
        return False, "cider is null"


def check_cider_ip(cider, ip):
    try:
        return ip in IPy.IP(cider)
    except:
        return False




if __name__ == '__main__':
    pass
# ips = ' ,'
# status, result = check_ips(ips)
# print status, result
