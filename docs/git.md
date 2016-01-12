GIT
====================


GIT Branches
----------------------------------

s2c2 related branches:
    * master: the main branch for s2c2 related code in dev (stopped active dev on 2015-08-24, see log)
    * production: the main branch for s2c2 code in production (stopped active dev on 2015-08-24, see log)

p2 related branches:
    * p2dev: the main dev branch for p2 (or servuno), currently maps to v2
    * p2prod: the main prod branch for p2, current maps to v2
    * p2/payment: the branch that evaluates payment options
    * p2/v2: the minimalist design before 3rd pivot (stopped active dev on 2015-09-30), using a list of links in the homepage (with "favor karma" data)
    * p2/v3: the pivot that targets to parents only, using FB-like tabs
    * p2/v4: the pivot to use Navbar links instead; separate PARENT/SITTER list; use TAG instead of PUBLIC/SUPERSET; migration squash; require invitation code.
    * p2/v5: merge PARENT/SITTER into PERSONAL, and use PUBLIC for TAG; make users/groups look consistent.
    * p2/v6: use 2 tabs: POST/DISCOVER. the design from the students.
    * i/*: branches for individual contributors


GIT Tags
----------------------------------

New tags:
  * p2-0.1: initial release, before "minimalist design" refactor.
  * p2-0.2: after the minimal design major refactor. changed theme

Outdated, only pertain to s2c2 related stuff:

  * backup-1:   before switching to a customized User model. (update: not going to switch to customized User model. use proxy instead)
  * backup-2:   before switching from customized User model, FullUser, back to Profile pattern. Also not using inheritance for "Group".
  * backup-3:   before using combined regular/date models for slot.
  * backup-4:   about to shrink the number of links and make everything in one big page (with tabs maybe).
  * rel-0.1:    initial offer for children's center
  * rel-0.1.1:  some fix based on rel-0.1
  * rel-0.2:    switched to fullcalendar
  * rel-0.2.1:  a few fixes before adding "message" system.
  * rel-0.3:    added message system
  * rel-0.4:    better assignment (arbitrary assignment)
