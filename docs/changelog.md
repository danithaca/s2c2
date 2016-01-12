Changelog
=====================

Only document major changes here.


*** 2015-11-04 ***

Ran through the process of creating a new database from scratch. Nothing special to note here. Just run migrate, and then load the fixtures.

Also squashed migrations.


*** 2015-09-30 ***

Now we are using the v3 design that stresses "parents-only" feature and separates parents list and babysitter list. And we don't allow babysitters sign up. This changed a lot from the original s2c2 design and the code will gets a lot of changes. Keeping the s2c2 old code is too much a liability and we are actually removing it in p2/v3 branch. Here is a list of things we will keep:

  * backup of data on production as fixtures.
  * SITE_ID structure: p2 as SITE_ID = 2

The goal is to make the code clean and agile. All old code can be found in the master branch and p2/v2 branch.


*** 2015-08-24 ***

The project started with __s2c2__ (scheduling software for children's center), but gradually moved focus to __p2__ (parents portal) for servuno. The original decision was to keep both s2c2 and p2 codes together in order to reuse code. Now it looks like keeping s2c2 code is more of a liability (preventing code change). The decision now is to remove s2c2 code, but keep the option open to add it back (i.e., keep the SITE_ID structure). This will make p2 more agile to move forward.

Even after code branch break up, both s2c2 and p2 are and will be sharing the same database.

We won't actively remove s2c2 code. The code break up just means that we don't care whether or not code changes to p2 would advertly affect s2c2.