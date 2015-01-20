class AddVoltsToMessages < ActiveRecord::Migration
  def change
    add_column :messages, :adc1, :decimal
    add_column :messages, :adc2, :decimal
    add_column :messages, :adc3, :decimal
    add_column :messages, :adc4, :decimal
    add_column :messages, :adc5, :decimal
    add_column :messages, :adc6, :decimal
    add_column :messages, :adc7, :decimal
    add_column :messages, :adc8, :decimal
  end
end
