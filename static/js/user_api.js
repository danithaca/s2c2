function initialize_user_api(tag_id) {
  'use strict';
  var user_api = {};

  user_api.User = Backbone.Model.extend({
    defaults: {}
  });

  user_api.UserList = Backbone.Collection.extend({
    model:  user_api.User,
    url:    '/user/api'
  });

  user_api.UserPictureView = Backbone.View.extend({
    tagName:  'li',
    //template: _.template('<a href="<%= profile_link %>" title="<%= display_name %>"><img src="<%= picture %>" alt="<%= display_name %>" class="img-circle user-picture-md"/></a>'),
    template: _.template('<img src="<%= picture %>" alt="<%= display_name %>" class="img-circle user-picture-md"/>'),

    render: function() {
      this.$el.html(this.template(this.model.toJSON()));
      return this;
    }
  });

  user_api.UserListView = Backbone.View.extend({
    el: tag_id,

    render: function(collection) {
      this.$el.empty();
      collection.each(function(user) {
        var userView = new user_api.UserPictureView({model: user});
        this.$el.append(userView.render().el);
      }, this);
    }
  });

  user_api.userList = new user_api.UserList();
  user_api.userListView = new user_api.UserListView();

  user_api.refresh = function(cid, start, end) {
    user_api.userList.fetch({
      success: function(collection) {
        user_api.userListView.render(collection);
      },
      data: { cid: cid, start: start, end: end }
    });
  };

  return user_api;
}