Feature: create/view a job for parents

  @core
  Scenario: access the link
    Given I am logged in as user "test@servuno.com" with password "password"
    When I follow "Post Job"
    Then I should be on "/job/post/favor/"


  @javascript
  Scenario: form submission
    Given I am logged in as user "test@servuno.com" with password "password"
    And I am on "/job/post/favor/"
    Then I should not see a "price" element
    When I fill in "description" with "help me"
    When I press "Post"
    And I press "OK"
    Then the URL should match "/job/\d+/"
    And I should see a ".match-summary" element
    And I should see "successfully"
    And I should not see "export to GCal"


  @javascript
  Scenario: wrong submission should see error message
    Given I am logged in as user "test@servuno.com" with password "password"
    And I am on "/job/post/favor/"
    When I fill in the following:
      | event_start | 12/01/2020 18:00 |
      | event_end   | 12/01/2020 17:00 |

    When I press "Post"
    And I press "OK"
    Then I should see "End date/time must be later than start date/time."

    When I fill in the following:
      | event_start | 12/01/2010 18:00 |
      | event_end   | 12/01/2010 17:00 |
    When I press "Post"
    And I press "OK"
    Then I should see "The date/time you specified cannot be in the past."


  Scenario: check email
    When I open the last email from "test@servuno.com" to "test1@servuno.com"
    Then check email contains "Template: contract/messages/match_engaged_normal"
    Then check email subject contains "John Smith"
    And check email contains "Compensation: $0"
    And check email contains "/job/response/"
    And check email contains "reciprocity"

