# Systema bot

how to setup database:

```
CREATE TABLE guildconfig(
id BIGINT,
mute_role BIGINT
);

CREATE TABLE prefixes(
id BIGINT,
prefix TEXT
);
```

env contains:

- TOKEN="bot token"
- PSQL_URI="postgresql path"
- OWNER_IDS="list of int separated with ;"
