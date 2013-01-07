# WikiBot

A super silly bot that reads the recent changes feed from MediaWiki and
forwards them to a notifico hook.

Modified to run on dotcloud

Run this to set the appropriate environment variables (replacing where necessary)

```
dotcloud env set NOTIFICO="<notifico hook url>" CATEGORY="<send notifications only for this category (not required)>" WIKI_FEEDURL="<Mediawiki recent changes feed url>"
```
