#include "record.h"


void Record::start_record(size_t n_element) {
    this->record_enabled = true;
    this->equity.reserve(n_element);
    this->capital_at_risk.reserve(n_element);
    this->concurrent_positions.reserve(n_element);
    this->time.reserve(n_element);
}


void Record::update() {
    if (!this->record_enabled) return;
    this->equity.push_back(this->state->equity);
    this->capital.push_back(this->state->capital);
    this->capital_at_risk.push_back(this->state->capital_at_risk);
    this->concurrent_positions.push_back(this->state->number_of_concurrent_positions);
    this->time.push_back(this->state->current_date);
}