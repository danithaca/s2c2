Feature: create/view/update/respond to a job for sitter

  @core
  Scenario: access the link
    Given I am logged in as user "test@servuno.com" with password "password"
    When I follow "Post Job"
    When I follow "Book a Babysitter"
    Then I should be on "/job/post/paid/"

  @core @javascript
  Scenario: UI without submission
    Given I am logged in as user "test@servuno.com" with password "password"
    And I am on "/job/post/paid/"
    Then the "price-info" field should contain "$10.00/hour, 1 hour"

    When I fill in the following:
      | event_start | 12/01/2020 18:00 |
      | event_end   | 12/01/2020 19:00 |
      | price       | 8                |
    Then the "price-info" field should contain "$8.00/hour, 1 hour"

    When I fill in "event_end" with "12/01/2020 20:00"
    Then the "price-info" field should contain "$4.00/hour, 2 hours"

    When I fill in "price" with "2"
    Then the "price-info" field should contain "$1.00/hour, 2 hours"

    When I fill in "event_start" with "12/01/2020 18:30"
    Then the "price-info" field should contain "$1.33/hour, 1 hour, 30 minutes"


  @javascript
  Scenario: form submission
    Given I am logged in as user "test@servuno.com" with password "password"
    And I am on "/job/post/paid/"
    When I fill in "description" with "help me"
    When I press "Post"
    And I press "OK"
    Then the URL should match "/job/\d+/"
    And I should see a ".match-summary" element
    And I should see "successfully"
    And I should not see "export to GCal"


  Scenario: check email
    When I open the last email from "test@servuno.com" to "test1@servuno.com"
    Then check email subject contains "John Smith needs help babysitting"
    And check email contains "Compensation: $10"
    And check email contains "Please respond if you can help or not"
    And check email contains "/job/response/"


  # form submission is not @core, so this cannot really be @core.
  Scenario: view upcoming
  # assuming after the first step of creating a contract (nearest time), we would see that same contract.
    Given I am logged in as user "test@servuno.com" with password "password"
    And I am on the homepage
    And I should see an ".engagement" element
    And I should see "$10"


  @javascript
  Scenario: view contract
    Given I am logged in as user "test@servuno.com" with password "password"
    And I am on the homepage
    When I click the ".engagement.engagement-headline" element
    Then the URL should match "/job/\d+/"
    And I should see "Edit"
    And I should see "Active"
    And I should see "Cancel"
    And I should see "Last updated"
    And I should see "test1"
    And I should see "John Smith's babysitter"
    And I should see a ".matches-tabs" element
    And I should see "Notified & Waiting"


  # let's assume test1 is also a babysitter
  @javascript
  Scenario: match response
    Given I am logged in as user "test1@servuno.com" with password "password"
    When I open the last email from "test@servuno.com" to "test1@servuno.com"
    When I follow the email link like "/job/response/"
    Then the URL should match "/job/response/\d+/"
    And I should see "John Smith"
    And I should see "Your response?"

    # first, try decline.
    When I fill in "match-response" with "message-i-declined"
    When I press "Decline"
    Then I should see "Declined"
    And I should see a "button[name='edit']" element
    # And I should not see a "button[name='match']" element
    Then the "button[name='match']" element is hidden
#    When I evaluate the following Javascript:
#      """
#      return $("button[name='match']").is(':hidden');
#      """
#    Then check Javascript result is true

    And the "match-response" field should contain "message-i-declined"
    When I evaluate the following Javascript:
      """
      return $('#match-response').attr('readonly') == 'readonly';
      """
    Then check Javascript result is true

    # check edit button
    When I press "Edit"
    And I should see "Accept"
    #And I should not see an "button[name='edit']" element
    Then the "button[name='edit']" element is hidden

    When I evaluate the following Javascript:
      """
      return $('#match-response').attr('readonly') != 'readonly';
      """
    Then check Javascript result is true

    # next, accept
    When I fill in "match-response" with "message-i-accepted-extra"
    When I press "Accept"
    Then I should see "Accepted"
    And the "match-response" field should contain "message-i-accepted-extra"

    When I press "Edit"
    When I fill in "match-response" with "message-i-accepted"
    When I press "Accept"
    Then I should see "Accepted"
    And the "match-response" field should contain "message-i-accepted"
    And the "match-response" field should not contain "message-i-accepted-extra"


  Scenario: check email
    When I open the last email
    Then check email sent from "test1@servuno.com" to "test@servuno.com"
    And check email subject contains "accepted your request"
    And check email contains "Review and confirm here"


  @javascript
  Scenario: edit contract, without submit
    Given I am logged in as user "test@servuno.com" with password "password"
    When I open the last email
    Then check email sent from "test1@servuno.com" to "test@servuno.com"
    When I follow the email link like "/job/"
    Then the URL should match "/job/\d+/"

    When I follow "Edit"
    Then the URL should match "/job/\d+/edit/"
    When I evaluate the following Javascript:
      """
      return $('#id_event_start').attr('readonly') == 'readonly' && $('#id_event_end').attr('readonly') == 'readonly';
      """
    Then check Javascript result is true


  @javascript
  Scenario: confirm contract
    Given I am logged in as user "test@servuno.com" with password "password"
    When I open the last email from "test1@servuno.com" to "test@servuno.com"
    When I follow the email link like "/job/"
    Then the URL should match "/job/\d+/"

    Then I should see a "div[data-slug='test1-bot']" element
    And I should see a "div[data-slug='test1-bot'] button.btn-success" element
    And I should see "message-i-accepted"

    When I click the "div[data-slug='test1-bot'] button.btn-success" element
    When I click the "button[data-bb-handler='confirm']" element
    Then I should see "Active - Confirmed"
    And I should see a "div[data-slug='test1-bot'] .label-success" element
    And I should see "Expired"
    And I should see "Undo"
    And I should see "export to GCal"


  Scenario: check confirmation email
    # give some time for celery to catch up.
    Then pause 10 seconds
    When I open the last email from "test@servuno.com" to "test1@servuno.com"
    Then check email subject contains "John Smith confirmed your offer"
    And check email contains "John Smith confirmed your offer of help. Details of the request"
    And check email contains "Please contact John directly if you need to change, cancel, or ask for more information. You can response to the email directly or use the following information"

    When I open the last email from "test1@servuno.com" to "test@servuno.com"
    Then check email subject contains "Confirmation"
    And check email contains "You have confirmed the offer from Test1 Bot."


  @javascript
  Scenario: undo and cancel
    Given I am logged in as user "test@servuno.com" with password "password"
    When I open the last email from "test1@servuno.com" to "test@servuno.com"
    When I follow the email link like "/job/"
    Then the URL should match "/job/\d+/"

    When I press "Undo"
    Then pause 1 second
    When I click the "button[data-bb-handler='confirm']" element

    # check email
    When I open the last email from "test@servuno.com" to "test1@servuno.com"
    Then check email subject contains "John Smith canceled your confirmed offer"

    When I press "Cancel"
    When I click the "button[data-bb-handler='confirm']" element
    Then I should see "Canceled"

    When I open the last email from "test@servuno.com" to "test1@servuno.com"
    Then check email subject contains "Request canceled"