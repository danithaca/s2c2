s2c2
====

Celery command:

```
celery worker -A p2 -l info --autoreload
```

Tags:

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