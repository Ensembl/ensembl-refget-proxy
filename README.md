## Ensembl Refget Proxy

- Python application to proxy against Ensembl refget services.


### Quick Start
- `$ git clone https://github.com/Ensembl/ensembl-refget-proxy.git`
- `$ cd ensembl-refget-proxy`
- `$ sudo docker-compose -f docker-compose.yml up`

To run as a daemon run:
- `$ sudo docker-compose -f docker-compose.yml up -d`

A working request sample working with current configurations:
- `http://0.0.0.0:8083/api/sequence/6681ac2f62509cfc220d78751b8dc524?start=1&end=20` 


## Deploy Notes
You can add and modify Refget server urls in `$REFGET_SERVER_URL_LIST` environment variable available in .env file. use `,` as separator.
`REFGET_SERVER_URL_LIST=https://www.refget-server-sample1.info/,http://refget-server-sample2.info/`
 
 


## Development
Use [Python Black](https://pypi.org/project/black/) package as code formatter.


## Background
 - [Refget is a GA4GH standard for retrieving sequences and metadata about said sequence from a checksum derived identifier](https://github.com/ga4gh/large-scale-genomics-wiki/blob/master/refget.md)
 