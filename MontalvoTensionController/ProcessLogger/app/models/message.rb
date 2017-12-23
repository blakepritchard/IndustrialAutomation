require 'twilio-ruby'

class Message < ActiveRecord::Base
  validates :process, :presence => true
  validates :sender, :presence => true

  before_save do
    x = JSON.parse(self.text)
    self.adc1 = x['ADC1']
  end


end
