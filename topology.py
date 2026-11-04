from mininet.topo import Topo
from mininet.node import Node
from mininet.link import TCLink


class LinuxRouter(Node):
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        if 'routes' in params:
            for (ip, gateway) in params['routes']:
                self.cmd('ip route add {} via {}'.format(ip, gateway))
        self.cmd('sysctl net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()


class courseworkTopo(Topo):

    def build(self):

        host1 = self.addHost('host1', ip="192.168.0.2/24",
                             defaultRoute='via 192.168.0.1')
        host2 = self.addHost('host2', ip="192.168.0.3/24",
                             defaultRoute='via 192.168.0.1')

        host3 = self.addHost('host3', ip="192.168.2.2/24",
                             defaultRoute='via 192.168.2.1')
        host4 = self.addHost('host4', ip="192.168.2.3/24",
                             defaultRoute='via 192.168.2.1')

        host5 = self.addHost('host5', ip="192.168.3.2/24",
                             defaultRoute='via 192.168.3.1')

        switch1 = self.addSwitch('switch1')
        switch2 = self.addSwitch('switch2')

        r1 = self.addHost('router1', cls=LinuxRouter, ip=None)
        r2 = self.addHost('router2', cls=LinuxRouter, ip=None)
        r3 = self.addHost('router3', cls=LinuxRouter, ip=None)

        self.addLink(host1, switch1)
        self.addLink(host2, switch1)
        self.addLink(host3, switch2)
        self.addLink(host4, switch2)

        # switch1 --> router1
        self.addLink(switch1, r1, intfName2='router1-eth1',
                     params2={'ip': '192.168.0.1/24'})

        # switch2 --> router2
        self.addLink(switch2, r2, intfName2='router2-eth1',
                     params2={'ip': '192.168.2.1/24'})

        # host5 --> r3
        self.addLink(host5, r3, intfName2='router3-eth0',
                     params2={'ip': '192.168.3.1/24'})

        # r1 <--> r2
        self.addLink(r1, r2,
                     intfName1='router1-eth2', params1={'ip': '10.10.0.1/24'},
                     intfName2='router2-eth2', params2={'ip': '10.10.0.2/24'},
                     cls=TCLink, delay='10ms', loss=1)

        # r1 <--> r3
        self.addLink(r1, r3,
                     intfName1='router1-eth3', params1={'ip': '10.10.1.1/24'},
                     intfName2='router3-eth2', params2={'ip': '10.10.1.2/24'},
                     cls=TCLink, bw=100, delay='100ms')

    def postBuild(self, net):
        r1 = net.get('router1')
        r2 = net.get('router2')
        r3 = net.get('router3')

        r1.cmd('ip route add 192.168.2.0/24 via 10.10.0.2')
        r1.cmd('ip route add 192.168.3.0/24 via 10.10.1.2')

        r2.cmd('ip route add 192.168.0.0/24 via 10.10.0.1')
        r2.cmd('ip route add 10.10.1.0/24 via 10.10.0.1')
        r2.cmd('ip route add 192.168.3.0/24 via 10.10.0.1')

        r3.cmd('ip route add 192.168.0.0/24 via 10.10.1.1')
        r3.cmd('ip route add 10.10.0.0/24 via 10.10.1.1')
        r3.cmd('ip route add 192.168.2.0/24 via 10.10.1.1')


# the topologies accessible to the mn tool's `--topo` flag
# note: if using the Dockerfile, this must be the same as in the Dockerfile
topos = {'courseworkTopo': (lambda: courseworkTopo())}
