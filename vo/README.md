# GAVO

This service exposes the SoFiAX_services database to TAP so that it is publicly accessible via VO-compliant tools.

## Tables

Edit the `vo.rd` file to change the tables in the database that will be exposed via the TAP service.

## Permissions

It is also necessary to change the permissions of the folder

```
chown -R gavo:gavo /var/gavo
```

## Basic Auth

To set up basic auth you will need to follow the instructions here which are available from the links below

Create a user and group in `dachs`

```
dachs admin adduser tapusers master_password
dachs admin adduser wallaby_user their_password
dachs admin addtogroup wallaby_user tapusers
```

On restart, it is necessary to recreate the `userconfig.rd` file. You can do this with the following commands:

```
cd `dachs config configDir`
dachs admin dumpDF //userconfig > userconfig.rd
```

Edit the `userconfig.rd` file on the line below `<NXSTREAM id="tapdescription">` with:

```
<limitTo>tapusers</limitTo>
```

then restart the service or run `dachs serve exp //tap` (note this gave me an error so I restarted my Docker container). The final step is to limit the query service to the users belonging to `tapusers` can access the system

```
mkdir -p /var/gavo/inputs/__system__
cd /var/gavo/inputs/__system__
dachs adm dumpDF //adql > adql.rd
```

and edit the `adql.rd` file to include the `limitTo="tapusers"` snippet such that

```
<service id="query" core="qcore" limitTo="tapusers">
```

## Links:

- http://docs.g-vo.org/DaCHS/howDoI.html#protect-my-tap-service-against-usage
- http://docs.g-vo.org/DaCHS/tutorial.html#the-userconfig-rd