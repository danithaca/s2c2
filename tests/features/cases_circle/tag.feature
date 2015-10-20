Feature: test features related to "tag" circles.

  @core
  Scenario: basic link
    Given I am logged in as user "test@servuno.com" with password "password"
    When I follow "Build Network"
    And I follow "Join Groups"
    Then I should be on "/connect/group/"
    And I should see "Browse all groups available"
    And I should see "Add New Group"

  @core @javascript
  Scenario: create new group
    Given I am logged in as user "test@servuno.com" with password "password"
    Given I am on "/connect/group/"
    When I click the "#button-add-group" element
    Then I should see a "#create-modal-form" element
    When I fill in the following:
      | Name        | Test internal (to be deleted)                           |
      | Description | This is a test group for internal testing purposes only |
      | Website     | http://google.com                                       |
    And I click the "#create-modal-form-submit" element
    Then I should be on "/connect/group/"
    And I should see "Test internal (to be deleted)"

    When I click the "#browse-all-link" element
    Then I should see "This is a test group for internal testing purposes only"
    And I should see a ".join-button" element

  @core @javascript
  Scenario: basic add/remove with select2
    Given I am logged in as user "test@servuno.com" with password "password"
    Given I am on "/connect/group/"
    When I click the "li.select2-selection__choice[title^='Test internal'] .select2-selection__choice__remove" element
    Then I should see "Changes are not saved"

    When I press "Save Changes"
    Then I should be on "/connect/group/"
    And I should not see a "li.select2-selection__choice[title^='Test internal']" element

    # this does not work. js can't trigger "click" on a "select" element.
#    When I run the following Javascript:
#      """
#      $('select[name="tags"]').select2('open');
#      $('li.select2-results__option:contains("Test internal")').click();
#      """

    When I additionally select "Test internal (to be deleted)" from "tags"
    Then I should see "Changes are not saved"
    When I press "Save Changes"
    Then I should be on "/connect/group/"
    And I should see a "li.select2-selection__choice[title^='Test internal']" element


  @core @javascript
  Scenario: join group using button
    Given I am logged in as user "test@servuno.com" with password "password"
    Given I am on "/connect/group/"
    # make sure the group is already added.
    And I should see a "li.select2-selection__choice[title^='Test internal']" element

    # update message
    When I click the "#browse-all-link" element
    Then I should see a "li[data-slug='test-internal-to-be-deleted']" element
    When I click the "li[data-slug='test-internal-to-be-deleted'] a" element
    Then I should see a "#join-modal-form" element
    When I fill in "note" with "message-note"
    And I click the "#join-modal-form-submit" element

    # check message is there. and leave group
    Then I should be on "/connect/group/"
    When I click the "#browse-all-link" element
    When I click the "li[data-slug='test-internal-to-be-deleted'] a" element
    Then I should see "message-note"
    And I click the "#join-modal-form-submit-alt" element

    # check left group, and re-join group
    Then I should be on "/connect/group/"
    And I should not see a "li.select2-selection__choice[title^='Test internal']" element
    When I click the "#browse-all-link" element
    When I click the "li[data-slug='test-internal-to-be-deleted'] a" element
    When I fill in "note" with "message-note"
    And I click the "#join-modal-form-submit" element
    Then I should be on "/connect/group/"
    And I should see a "li.select2-selection__choice[title^='Test internal']" element


  @core @javascript
  Scenario: group page join
    Given I am logged in as user "test1@servuno.com" with password "password"
    Given I am on "/connect/group/"
    # join group first
    When I additionally select "Test internal (to be deleted)" from "tags"
    When I press "Save Changes"
    When I click the "li.select2-selection__choice[title^='Test internal'] .hover-pointer" element
    Then the url should match "/connect/group/\d+/"

    Then I should see "Test Internal"
    # this is from test@servuno.com
    And I should see "message-note"
    # no permission to add
    And I should not see a "#new-item-add-btn" element
    And I should not see a ".destroy.hover-pointer" element

    When I click the "a.join-button" element
    Then I should see a "#join-modal-form" element
    When I fill in "note" with "message-note-test2"
    And I click the "#join-modal-form-submit" element

    # check message is there. and leave group
    Then the url should match "/connect/group/\d+/"
    When I click the "a.join-button" element
    Then I should see "message-note-test2"
    And I click the "#join-modal-form-submit-alt" element

    # check left group, and re-join group
    Then the url should match "/connect/group/\d+/"
    When I click the "a.join-button" element
    Then I should see "Join Group"
    When I fill in "note" with "message-note-test2"
    And I click the "#join-modal-form-submit" element
    Then I should see "Member"

  @javascript
  Scenario: group page admin
    Given I am logged in as user "test@servuno.com" with password "password"
    Given I am on "/connect/group/"
    When I click the "li.select2-selection__choice[title^='Test internal'] .hover-pointer" element
    Then the url should match "/connect/group/\d+/"

    # should see admin elements
    Then I should see a "#new-item-add-btn" element
    And I should see a ".destroy.hover-pointer" element
    And I should see a "#group-edit-button" element

    # edit group
    When I click the "#group-edit-button" element
    Then I should see a "#edit-group-modal-form" element
    And I should see "Edit Group"
    And the "Website" field should contain "http://google.com"
    When I click the "#edit-group-modal-form-submit" element
    Then the url should match "/connect/group/\d+/"

    # remove contact
    When I click the "div[data-email='test1@servuno.com'] .destroy" element
    Then I should see "Changes are not saved"
    And I press "Save Changes"
    Then the url should match "/connect/group/\d+/"
    And I should not see a "div[data-email='test1@servuno.com']" element

    # todo: test invite


  @core
  Scenario: clean up
    Given I am logged in as admin
    And I am on "/admin/circle/circle/"
    When I follow "Test internal (to be deleted)"
    And I follow "Delete"
    And I press "Yes, I'm sure"
    Then I should see "was deleted successfully"
