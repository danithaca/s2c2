Design Documentation
===============================


Timezone concerns
-----------------

Each user/location is associated with one and only one "area". The area has timezone information.

DayToken/TimeToken do *NOT* care about timezone. They are assumed to be exchangible to textual "tokens", and always agrees with the user's local time. They don't change when Daylight Saving Time changes.

Any DateTimeField needs to care about timezone. They save the exact time something happends.

We use America/Detroit as the default timezone for the backend. In MVP, we don't need to care.


Locations, Classrooms, Centers, Areas, Staff, Managers
------------------------------------------------------

"Area" is like Drupal's organic group. Everything belongs to an area (directly or indirectly).
Centers belong to a single area.
Classrooms belong to a single center.
Managers/Staff belong to one or multiple centers.
Managers have access to all classrooms of the centers they belong to.
Staff are shown in classrooms of all centers.
