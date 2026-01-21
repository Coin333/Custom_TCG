#include "../include/Ability.h"
#include <sstream>

Ability::Ability(const std::string& name,
                 const std::string& description,
                 AbilityType type,
                 TargetType target,
                 int value,
                 int cost_modifier,
                 int duration)
    : name(name), description(description), type(type), target(target),
      value(value), cost_modifier(cost_modifier), duration(duration) {
}

bool Ability::canUse(int current_energy) const {
    return current_energy >= cost_modifier;
}

std::string Ability::toString() const {
    std::ostringstream oss;
    oss << name;
    if (value != 0 || cost_modifier != 0) {
        oss << " (";
        if (value != 0) {
            oss << "Value: " << value;
        }
        if (cost_modifier != 0) {
            if (value != 0) oss << ", ";
            oss << "Cost: " << cost_modifier;
        }
        oss << ")";
    }
    if (!description.empty()) {
        oss << " - " << description;
    }
    return oss.str();
}
