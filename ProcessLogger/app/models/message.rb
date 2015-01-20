class Message < ActiveRecord::Base
  validates :process, :presence => true
  validates :sender, :presence => true




end
