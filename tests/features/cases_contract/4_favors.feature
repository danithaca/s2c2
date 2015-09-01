Feature: Test favors exchange

  @javascript
  Scenario: create contract and confirm, set up history
    # create test user
    Given I am logged in as user "test2@servuno.com" with password "password"
    And I am on "/circle/manage/personal"
    When I fill in "new-contact" with "to-be-deleted-favors@servuno.com"
    And I press "new-contact-add-btn"
    Then I should see "to-be-deleted-favors@servuno.com"
    When I press "Submit"

    # create contract
    Given I am on "/contract/add/"
    When I fill in "price" with "0"
    And I press "Submit"
    And I press "OK"
    And pause 3 seconds

    # respond from email. login token should take care of login
    When I open the last email from "test2@servuno.com" to "to-be-deleted-favors@servuno.com"
    And I follow the email link like "/contract/match/"
    Then the URL should match "/contract/match/\d+/"
    And I should see "Previous interactions: - None -"
    And I should see "Favors karma: - None -"
    When I press "Accept"
    And pause 3 seconds
    # Given I am on "/account/logout/"

    # confirm from email. login token should take care of login
    When I open the last email from "to-be-deleted-favors@servuno.com" to "test2@servuno.com"
    And I follow the email link like "/contract/"
    Then the URL should match "/contract/\d+/"
    When I press "Confirm"
    And I press "Yes"

    # login as admin and modify event time.
    Given I am on "/account/logout/"
    And I am logged in as admin
    And I am on "/admin/contract/contract/"
    When I run the following Javascript:
      """
      $('#result_list th.field-id:first a')[0].click();
      """
    Then the URL should match "/admin/contract/contract/\d+/"
    When I fill in the following:
      | event_start_0 | 2010-12-10 |
      | event_end_0   | 2010-12-10 |
    And I press "Save"

    # mark as success
    Then I follow the email link like "/contract/"
    Then the URL should match "/contract/\d+/"
    And I should see "Done"
    When I press "Successful"
    Then pause 1 second

    # now there is a favor from to-be-deleted to test2


  @javascript
  Scenario: review favors info
    Given I am logged in as user "test2@servuno.com" with password "password"
    Given I am on "/contract/add/"
    When I fill in "price" with "0"
    And I press "Submit"
    And I press "OK"
    And pause 3 seconds

    When I open the last email from "test2@servuno.com" to "to-be-deleted-favors@servuno.com"
    And I follow the email link like "/contract/match/"
    Then the URL should match "/contract/match/\d+/"
    And I should see "Previous interactions: You (to-be-del...) helped Nancy 1 time"
    And I should see "Favors karma: Nancy owes you (to-be-del...) 1 favor"

    # now logged in as to-be-deleted from login token
    # try the other way: to-be-deleted send request to test2
    Given I am on "/circle/manage/personal"
    When I fill in "new-contact" with "test2@servuno.com"
    And I press "new-contact-add-btn"
    Then I should see "test2@servuno.com"
    When I press "Submit"
    Given I am on "/contract/add/"
    When I fill in "price" with "0"
    And I press "Submit"
    And I press "OK"
    And pause 3 seconds
    When I open the last email from "to-be-deleted-favors@servuno.com" to "test2@servuno.com"
    And I follow the email link like "/contract/match/"
    Then the URL should match "/contract/match/\d+/"
    Then I should see "You owe to-be-deleted-favors a favor. Please consider return the favor by accepting the request"
    And I should see "Previous interactions: to-be-del... helped you (Nancy) 1 time"
    And I should see "Favors karma: You (Nancy) owe to-be-del... 1 favor "

    # now logged in as nancy from login_token


  Scenario: clean up - remove user
    Given I am logged in as admin
    And I am on "/admin/auth/user"
    When I follow "to-be-deleted-favors"
    And I follow "Delete"
    And I press "Yes, I'm sure"
    Then I should see "was deleted successfully"