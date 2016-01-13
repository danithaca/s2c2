Design Documentation
====================

Design and architecture decisions are documented here. __Caveat__: The code evolves over time as we change features and might not be as clean.


Social Connections
------------------

Code related to social connections, building network, joining groups, etc., is in the `circle` app. A personal network or a public social group is coded as `Circle`. A user can be added into a `Circle` through `Membership`. Important models are discussed below.

#### `Circle`

The field `type` specifies whether a `circle` instance is personal or public. A personal `circle` is a user's personal network in an `area`. Usually there is only one personal `circle` for one user in an `area` (but the user might have other personal circles in other areas). The field `owner` specifies which user the personal circle belongs to, and will not change. A public `circle` is a "Social Group". Its `owner` is usually the user who created the circle, but could be transferred to another user.

The field `area` specifies which city or geological location this `circle` belongs to. Right now it's only Ann Arbor, MI. Once the business expands to other cities, this field could take other values.

The field `mark_agency` and `mark_approved` only applies to a public `circle`. "Agency" is a special type of public circle, where it is maintained by professional agencies to provide babysitters. It is different from a regular public circle, where the goal is to have parents socialize with each other. An example of an "agency" circle is "University of Michigan Family Helpers". The field `mark_approved` is needed because we need to review user created public circles and approve or disapprove.

The method `to_proxy` convert a generic `Circle` instance to either a `PersonalCircle` proxy instance, or a `PublicCircle` proxy instance.

#### Membership

A user is added to a `circle` through a `Membership` instance. The field `member` specifies the user, and `circle` specifies the circle.

A user/member in a circle could either be a parent or a babysitter. This is stored in the `as_role` field.

If the member is able to admin the circle, then the field `as_admin` is set to `True`.

The status of the membership is specified by two fields: `active` and `approved`. For the public circle, when a member requests to join it, `active` would be set to `True`, but `approved` remains `None`. When the public circle's owner or admin approves the membership, then `approved` would be set to `True`; or if the membership is blocked, then `approved` is set to `False`. When the member leaves the public circle, `active` is set to `False` (instead of deleting the `Membership` instance).

For the personal circle. When a circle's owner A adds another user B to A's personal network, the field `active` is set to `True` while `approved` remains `None`. When B approves A's friendship request, then `approved` is set to `True`; or if blocked, `approved` is set to `False`. When A removes B from his personal network, then `active` is set to `False` (instead of removing the `Membership` instance). Note that if B is added as a parent (instead of a babysitter), that implies that B also agrees to add A as a parent. In other words, the relationship between A and B is symmetric: in order for A and B to establish a relationship, both A and B needs to approve. We'll discuss more in `Friendship`. On the other hand, if B is added as a babysitter, the relationship is not symmetric. That is, B doesn't have to add A into B's personal network.

#### UserConnection

`UserConnection` is not a db model. It's a utility class to help manage the connection between two users: `initiate_user` and `target_user`. For example, if we want to know the trust level between user A and user B, we would create a `UserConnection` instance and use the `trust_level()` method to calculate.

#### Friendship

`Friendship` is a sub-class of `UserConnection`. It's used for a special case of `UserConnection`, where the connection between A and B is symmetric. Think of Facebook's user connection as "symmetric", where if A is B's friend, then B is also A's friend; whereas Twitter's user connection is "asymmetric", where A follows B doesn't imply B follows A. The `Friendship` instance helps enforce the "symmetric" connection between A and B -- if A adds B into A's personal circle, then B will need to automatically adds A into B's personal circle.


Job Posts
---------

Code related to making job posts is in the `contract` app. Important db models are discussed below.


#### Contract

Each job post (created from "Get Help", "Offer Help", or "Book Help") is an instance of `Contract` model. The field `initiate_user` specifies which user created the `contract` instance.

`status` specifies which stage the `contract` is at. `INITIATED` is when the contrat is first created. `ACTIVE` is when payment is done (will be added later) and the system is search for a match. `CONFIRMED` is when the `initiate_user` confirmed a match (`Match` will be discussed next). `SUCCESSFUL` and `FAILED` is the feedback from `initiate_user` after the contract is done.

`confirmed_match` specifies which `Match` is confirmed. It is only valid when the status reached `CONFIRMED`.

`audience_type` and `audience_data` are used to make remmendations of `Match` to a `Contract`.

`price` specifies whether the job requires payment. "Get Help" and "Offer Help" usually have `price=0`; while "Book Help" usually have `price>0`.

`area`: which city/location the `contract` happens.

`reverse` is a special mark. It means the `contract` is not to find help, but to offer help. In this case, the `initiate_user` is the one who offers help to the `Match.target_user`. We need to know who's offering help in order to calculate favors.


#### Match

A `Match` instance stores which user is contacted regarding a `Contract` (job post), and the user's response. One `Contract` instance is associated with multiple `Match` objects. In a `Match` instance, `target_user` stores which user is contacted, `status` stores the user's response, `response` stores the textual response from `target_user`.

If the `initiate_user` select "Automatic choosing target" when creating a `contract`, then the system will automatically create `match` objects for the `contract`. This is done in `algorithm.py`, which we'll use more advanced "recommendation" algorithms to handle in the future.


#### Engagement

We use `Engagement` to model the engagement between `initiate_user` in `Contract` and `target_user` in `Match`. Sometimes we don't care about whether a user is engaged in a babysitting activity because he is an `initiate_user` or a `target_user`. Then we would use `Engagement`.


Timezone concerns
-----------------

Each user/location is associated with one and only one "area". The area has timezone information.

~~DayToken/TimeToken do *NOT* care about timezone. They are assumed to be exchangible to textual "tokens", and always agrees with the user's local time. They don't change when Daylight Saving Time changes.~~

Any DateTimeField is timezone-aware. It has the exact timestamp of something occurred.

We use America/Detroit as the default timezone for the backend. Need to test how it works in Pacific timezone.


(OBSOLETE) Locations, Classrooms, Centers, Areas, Staff, Managers
-----------------------------------------------------------------

"Area" is like Drupal's organic group. Everything belongs to an area (directly or indirectly).
Centers belong to a single area.
Classrooms belong to a single center.
Managers/Staff belong to one or multiple centers.
Managers have access to all classrooms of the centers they belong to.
Staff are shown in classrooms of all centers.
