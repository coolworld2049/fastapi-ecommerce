rs.initiate({_id: "rs-config-server", configsvr: true, version: 1, members: [{_id: 0, host: 'store_service_configsvr01:27017'}]})