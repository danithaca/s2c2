Feature: Test Find (contract add)

  @core
  Scenario: access the link
    Given I am logged in as user "test@servuno.com" with password "password"
    When I follow "Find a Babysitter"
    Then I should be on "/contract/add/"


  @core @javascript
  Scenario: UI without submission
    Given I am logged in as user "test@servuno.com" with password "password"
    And I am on "/contract/add/"
    Then the "#price-info-container" element is hidden
    And the checkbox "price-favor" should be unchecked

    When I fill in the following:
      | event_start | 12/01/2020 18:00 |
      | event_end   | 12/01/2020 19:00 |
      | price       | 8                |
    Then I should see a "#price-info-container" element
    And I should see a "#price-info" element
    Then the "price-info" field should contain "$8.00/hour, 1 hour"
    And the checkbox "price-favor" should be unchecked

    When I fill in "event_end" with "12/01/2020 20:00"
    Then the "price-info" field should contain "$4.00/hour, 2 hours"

    When I check "price-favor"
    Then the "price" field should contain "0"
    When I uncheck "price-favor"
    Then the "price" field should not contain "0"

    When I fill in "price" with "2"
    Then the "price-info" field should contain "$1.00/hour, 2 hours"

    When I fill in "event_start" with "12/01/2020 18:30"
    Then the "price-info" field should contain "$1.33/hour, 1 hour, 30 minutes"

    When I fill in "price" with "0"
    Then the "price-info" field should contain "favor exchange, 1 hour, 30 minutes"
    And the checkbox "price-favor" should be checked

    When I fill in "price" with ""
    Then the "#price-info-container" element is hidden


  @javascript
  Scenario: form submission
    Given I am logged in as user "test@servuno.com" with password "password"
    And I am on "/contract/calendar/"
    When I run the following Javascript:
      """
      var start = moment().add({hours: 1});
      var end = moment(start).add({hours: 1});
      $('#calendar').fullCalendar('select', start, end);
      """
    Then I should be on "/contract/add/"

    When I fill in "price" with "10"
    Then the "price-info" field should contain "$10.00/hour, 1 hour"

    When I press "Submit"
    And I press "OK"
    Then the URL should match "/contract/\d+/"
    And I should see a ".match-summary" element
    And I should see "successfully"


  @core @javascript
  Scenario: form submission for production using test2 who don't have any contact.
    Given I am logged in as user "test2@servuno.com" with password "password"
    And I am on "/contract/calendar/"
    When I run the following Javascript:
      """
      var start = moment().add({hours: 1});
      var end = moment(start).add({hours: 1});
      $('#calendar').fullCalendar('select', start, end);
      """
    Then I should be on "/contract/add/"

    When I fill in "price" with "10"
    Then the "price-info" field should contain "$10.00/hour, 1 hour"

    When I press "Submit"
    And I press "OK"
    Then the URL should match "/contract/\d+/"
    And I should see "successfully"


  @javascript
  Scenario: wrong submission should see error message
    Given I am logged in as user "test@servuno.com" with password "password"
    And I am on "/contract/add/"
    When I fill in the following:
      | event_start | 12/01/2020 18:00 |
      | event_end   | 12/01/2020 17:00 |
      | price       | 8                |

    When I press "Submit"
    And I press "OK"
    Then I should see "End date/time must be later than start date/time."

    When I fill in the following:
      | event_start | 12/01/2010 18:00 |
      | event_end   | 12/01/2010 17:00 |
      | price       | 8                |

    When I press "Submit"
    And I press "OK"
    Then I should see "The date/time you specified cannot be in the past."


  Scenario: check email
    When I open the last email from "test@servuno.com" to "test1@servuno.com"
    Then check email subject contains "John Smith needs help babysitting (for a fee)"
    And check email contains "Compensation: $10"
    And check email contains "Please respond if you can help or not"
    And check email contains "/contract/match/"
