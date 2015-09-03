Feature: Edit account
  In order to change my personal info
  As a logged in user
  I need to update my account info

  @core
  Scenario: edit account
    Given I am logged in as user "test@servuno.com" with password "password"
    When I follow "Edit account"
    Then the "First name" field should contain "John"
    And the "First name" field should not contain "Daniel"

    When I fill in the following:
      | First name | Daniel       |
      | Last name  | Zhou         |
      | Phone      | 734-123-4567 |
      | About me   | This is me.  |
    And I press "Submit"
    Then I should see "Profile successfully updated."
    Given I am on "/account/edit/"
    Then the "First name" field should contain "Daniel"
    And the "Last name" field should contain "Zhou"
    And the "Phone" field should contain "734-123-4567"
    # And the "About me" field should contain "This is me."

    # revert changes.
    When I fill in the following:
      | First name | John                    |
      | Last name  | Smith                   |
      | Phone      | 555-555-5555            |
      | About me   | This is a test account. |
    And I press "Submit"
    Then I should see "Profile successfully updated."
    Given I am on "/account/edit/"
    And the "First name" field should contain "John"


  @core
  Scenario: view account
    Given I am logged in as user "test@servuno.com" with password "password"
    When I follow "View Account"
    Then I should be on "/account/"
    And I should see "John Smith"
    And I should see "John's Contacts"
    And I should see "John's Circles"
    And I should see "Listed By"
    And I should see "test@servuno.com"
    And I should see "555-555-5555"
    And I should see "This is a test account."

    When I follow "link_account_picture"
    Then I should be on "/account/picture/"

    When I move backward one page
    When I follow "link_account_edit"
    Then I should be on "/account/edit/"

    When I move backward one page
    When I follow "link_manage_personal"
    Then I should be on "/circle/manage/personal/"

    When I move backward one page
    When I follow "link_manage_public"
    Then I should be on "/circle/manage/public/"

    When I move backward one page
    When I follow "link_manage_loop"
    Then I should be on "/circle/manage/loop/"