# GAVO

This service exposes the SoFiAX_services database to TAP so that it is publicly accessible via VO-compliant tools.

## Configuration

The DaCHS configuration files (`gavo.rc`, `dsn`, `feed`, `trustedquery`, `untrustedquery`, `defaultmeta.txt` and the parts of `vo.rd`) are templates in the `templates` folder. On startup `render-config.sh` fills in the `${VARIABLE}` placeholders from the environment and writes the files to where DaCHS expects them. The variables and their defaults are listed in [`.env.example`](../.env.example).

## Tables

The resource descriptor `vo.rd` is assembled on startup from `templates/header.rd`, one file in `templates/modules` for each module listed in the `MODULES` environment variable, and `templates/footer.rd`.

| Module | Tables |
|---|---|
| `core` | `run`, `instance`, `detection` and the datalink services for products |
| `metadata` | `comment`, `tag`, `tag_detection` |
| `operations` | `observation` |
| `wallaby_operations` | `tile`, `tile_obs`, `source_extraction_region`, `source_extraction_region_tile` (requires `operations`) |
| `wallaby_kinematics` | `kinematic_model`, `kinematic_model_3kidnas` |

`core` is always required. To expose a new table add it to a module, or create a new file in `templates/modules` with its own `<data>` element.

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