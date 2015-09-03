Feature: view contacts

  Scenario: attention icon and "isolated" message
    Given I am logged in as user "test@servuno.com" with password "password"
    And I am on "/dashboard/"
    Then I should not see a ".dashboard-link[data-slug='manage-contacts'] .attention-icon" element
    Given I am on "/contract/add/"
    Then I should not see "You have few contacts on Servuno. Please add more contacts and/or join more parents circles."
    Given I am on "/account/logout/"
    # this user is under represented.
    Given I am logged in as user "test2@servuno.com" with password "password"
    And I am on "/dashboard/"
    Then I should see a ".dashboard-link[data-slug='manage-contacts'] .attention-icon" element
    Given I am on "/contract/add/"
    Then I should see "You have few contacts on Servuno. Please add more contacts and/or join more parents circles."