package discovery

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"time"

	"go.etcd.io/etcd/clientv3"
	"google.golang.org/grpc/resolver"
)

type EtcdRegistry struct {
	client   *clientv3.Client
	prefix   string
	ttl      int64
	leaseID  clientv3.LeaseID
	stopChan chan struct{}
}

type ServiceInfo struct {
	Name     string `json:"name"`
	Address  string `json:"address"`
	Port     int    `json:"port"`
	Metadata map[string]string `json:"metadata"`
}

func NewEtcdRegistry(endpoints []string, prefix string, ttl int64) (*EtcdRegistry, error) {
	client, err := clientv3.New(clientv3.Config{
		Endpoints:   endpoints,
		DialTimeout: 5 * time.Second,
	})
	if err != nil {
		return nil, err
	}

	return &EtcdRegistry{
		client:   client,
		prefix:   prefix,
		ttl:      ttl,
		stopChan: make(chan struct{}),
	}, nil
}

func (r *EtcdRegistry) Register(ctx context.Context, service ServiceInfo) error {
	// Create a lease
	lease, err := r.client.Grant(ctx, r.ttl)
	if err != nil {
		return err
	}
	r.leaseID = lease.ID

	// Serialize service info
	data, err := json.Marshal(service)
	if err != nil {
		return err
	}

	// Put service info with lease
	key := fmt.Sprintf("%s/%s/%s:%d", r.prefix, service.Name, service.Address, service.Port)
	_, err = r.client.Put(ctx, key, string(data), clientv3.WithLease(r.leaseID))
	if err != nil {
		return err
	}

	// Keep alive
	ch, kaerr := r.client.KeepAlive(ctx, r.leaseID)
	if kaerr != nil {
		return kaerr
	}

	go func() {
		for {
			select {
			case <-r.stopChan:
				return
			case <-ch:
				// Keep alive response
			}
		}
	}()

	log.Printf("Service %s registered at %s:%d", service.Name, service.Address, service.Port)
	return nil
}

func (r *EtcdRegistry) Deregister() error {
	r.stopChan <- struct{}{}
	if r.leaseID != 0 {
		_, err := r.client.Revoke(context.Background(), r.leaseID)
		return err
	}
	return nil
}

func (r *EtcdRegistry) Discover(serviceName string) ([]ServiceInfo, error) {
	key := fmt.Sprintf("%s/%s/", r.prefix, serviceName)
	resp, err := r.client.Get(context.Background(), key, clientv3.WithPrefix())
	if err != nil {
		return nil, err
	}

	var services []ServiceInfo
	for _, kv := range resp.Kvs {
		var service ServiceInfo
		if err := json.Unmarshal(kv.Value, &service); err != nil {
			continue
		}
		services = append(services, service)
	}

	return services, nil
}

// Custom resolver for gRPC
type etcdResolver struct {
	registry *EtcdRegistry
	target   resolver.Target
	cc       resolver.ClientConn
}

func (r *etcdResolver) ResolveNow(resolver.ResolveNowOptions) {
	services, err := r.registry.Discover(r.target.Endpoint())
	if err != nil {
		r.cc.ReportError(err)
		return
	}

	var addrs []resolver.Address
	for _, service := range services {
		addr := fmt.Sprintf("%s:%d", service.Address, service.Port)
		addrs = append(addrs, resolver.Address{Addr: addr})
	}

	r.cc.UpdateState(resolver.State{Addresses: addrs})
}

func (r *etcdResolver) Close() {}