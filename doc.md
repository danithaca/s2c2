Development Documentation
=========================

Timezone concerns
-----------------

Each user/location is associated with one and only one "area". The area has timezone information.


Locations, Classrooms, Centers, Areas, Staff, Managers
------------------------------------------------------

"Area" is like Drupal's organic group. Everything belongs to an area (directly or indirectly).
Centers belong to a single area.
Classrooms belong to a single center.
Managers/Staff belong to one or multiple centers.
Managers have access to all classrooms of the centers they belong to.
Staff are shown in classrooms of all centers.