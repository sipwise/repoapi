tracker
=======

This app is taking care of the migration from ``TT#`` to ``MT#`` prefixes
due the migration from workfront to mantis service.

There are some helper commands that were executed in the import process but
mainly nowadays is just taking care of the conversion of URLs from workfornt
to mantis.

We have a nginx serving ``sipwise.my.workfront.com`` and that get redirected to
repoapi that will respond with a 302 to the proper Mantis URL.

```puppet
profile::gerrit::parameters::mantis_url: 'https://support.sipwise.com/view.php?id=$2'
profile::gerrit::parameters::workfront_url: 'https://repoapi.mgm.sipwise.com/tracker/mapper/task/$2'
```
