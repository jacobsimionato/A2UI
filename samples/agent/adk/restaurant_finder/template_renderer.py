from typing import List, Dict, Any
from ui_schema import LLMOutput, RestaurantListData, BookingFormData, ConfirmationData, Widget
from a2ui_validator import validate_a2ui_messages

def render_ui(llm_output: LLMOutput, base_url: str) -> List[Dict[str, Any]]:
    messages = []
    for widget in llm_output.widgets:
        if widget.type == "restaurant_list":
            messages.extend(render_restaurant_list(RestaurantListData(**widget.data), base_url))
        elif widget.type == "booking_form":
            messages.extend(render_booking_form(BookingFormData(**widget.data), base_url))
        elif widget.type == "confirmation":
            messages.extend(render_confirmation(ConfirmationData(**widget.data), base_url))
        else:
            # Log warning or raise error for unknown type
            pass
    # TODO: Add validation step here
    # validate_a2ui_messages(messages)
    return messages


def _create_data_model_items(restaurants: List[Restaurant]) -> List[Dict[str, Any]]:
    items = []
    for i, r in enumerate(restaurants):
        items.append({
            "key": f"item{i + 1}",
            "valueMap": [
                {"key": "name", "valueString": r.name},
                {"key": "rating", "valueString": r.rating},
                {"key": "detail", "valueString": r.detail},
                {"key": "infoLink", "valueString": r.infoLink},
                {"key": "imageUrl", "valueString": r.imageUrl},
                {"key": "address", "valueString": r.address},
            ]
        })
    return items

def render_restaurant_list(data: RestaurantListData, base_url: str) -> List[Dict[str, Any]]:
    surface_id = "restaurant_list"
    begin_rendering = {
        "beginRendering": {
            "surfaceId": surface_id,
            "root": "root-column",
            "styles": {"primaryColor": "#007BFF", "font": "Roboto"}
        }
    }

    components = [
        {"id": "root-column", "component": {"Column": {"children": {"explicitList": ["title-heading", "item-list"]}}}},
        {"id": "title-heading", "component": {"Text": {"usageHint": "h1", "text": {"path": "/title"}}}},
        {"id": "item-list", "component": {"List": {"direction": "vertical", "children": {"template": {"componentId": "item-card-template", "dataBinding": "/items"}}}}},
        {"id": "item-card-template", "component": {"Card": {"child": "card-layout"}}},
        {"id": "card-layout", "component": {"Row": {"children": {"explicitList": ["template-image", "card-details"]}}}},
        {"id": "template-image", "weight": 1, "component": {"Image": {"url": {"path": "imageUrl"}, "fit": "cover"}}},
        {"id": "card-details", "weight": 2, "component": {"Column": {"children": {"explicitList": ["template-name", "template-rating", "template-detail", "template-link", "template-book-button"]}}}},
        {"id": "template-name", "component": {"Text": {"usageHint": "h3", "text": {"path": "name"}}}},
        {"id": "template-rating", "component": {"Text": {"text": {"path": "rating"}}}},
        {"id": "template-detail", "component": {"Text": {"text": {"path": "detail"}}}},
        {"id": "template-link", "component": {"Text": {"text": {"path": "infoLink"}}}},
        {"id": "template-book-button", "component": {"Button": {"child": "book-now-text", "primary": True, "action": {"name": "book_restaurant", "context": [
            {"key": "restaurantName", "value": {"path": "name"}},
            {"key": "imageUrl", "value": {"path": "imageUrl"}},
            {"key": "address", "value": {"path": "address"}}
        ]}}}},
        {"id": "book-now-text", "component": {"Text": {"text": {"literalString": "Book Now"}}}}
    ]

    surface_update = {
        "surfaceUpdate": {
            "surfaceId": surface_id,
            "components": components
        }
    }

    data_model_update = {
        "dataModelUpdate": {
            "surfaceId": surface_id,
            "path": "/",
            "contents": [
                {"key": "title", "valueString": "Found Restaurants"},
                {"key": "items", "valueMap": _create_data_model_items(data.restaurants)}
            ]
        }
    }

    return [begin_rendering, surface_update, data_model_update]
def render_booking_form(data: BookingFormData, base_url: str) -> List[Dict[str, Any]]:
    surface_id = "booking_form"
    begin_rendering = {
        "beginRendering": {
            "surfaceId": surface_id,
            "root": "booking-form-column",
            "styles": {"primaryColor": "#007BFF", "font": "Roboto"}
        }
    }

    components = [
        {"id": "booking-form-column", "component": {"Column": {"children": {"explicitList": ["booking-title", "restaurant-image", "restaurant-address", "party-size-field", "datetime-field", "dietary-field", "submit-button"]}}}},
        {"id": "booking-title", "component": {"Text": {"usageHint": "h2", "text": {"path": "/title"}}}},
        {"id": "restaurant-image", "component": {"Image": {"url": {"path": "/imageUrl"}}}},
        {"id": "restaurant-address", "component": {"Text": {"text": {"path": "/address"}}}},
        {"id": "party-size-field", "component": {"TextField": {"label": {"literalString": "Party Size"}, "text": {"path": "/partySize"}, "textFieldType": "number"}}},
        {"id": "datetime-field", "component": {"DateTimeInput": {"value": {"path": "/reservationTime"}, "enableDate": True, "enableTime": True}}},
        {"id": "dietary-field", "component": {"TextField": {"label": {"literalString": "Dietary Requirements"}, "text": {"path": "/dietary"}, "textFieldType": "longText"}}},
        {"id": "submit-button", "component": {"Button": {"child": "submit-reservation-text", "primary": True, "action": {"name": "submit_booking", "context": [
            {"key": "restaurantName", "value": {"path": "/restaurantName"}},
            {"key": "partySize", "value": {"path": "/partySize"}},
            {"key": "reservationTime", "value": {"path": "/reservationTime"}},
            {"key": "dietary", "value": {"path": "/dietary"}},
            {"key": "imageUrl", "value": {"path": "/imageUrl"}}
        ]}}}},
        {"id": "submit-reservation-text", "component": {"Text": {"text": {"literalString": "Submit Reservation"}}}}
    ]

    surface_update = {
        "surfaceUpdate": {
            "surfaceId": surface_id,
            "components": components
        }
    }

    data_model_update = {
        "dataModelUpdate": {
            "surfaceId": surface_id,
            "path": "/",
            "contents": [
                {"key": "title", "valueString": f"Book a Table at {data.restaurantName}"},
                {"key": "address", "valueString": data.address},
                {"key": "restaurantName", "valueString": data.restaurantName},
                {"key": "partySize", "valueString": "2"},
                {"key": "reservationTime", "valueString": ""},
                {"key": "dietary", "valueString": ""},
                {"key": "imageUrl", "valueString": data.imageUrl}
            ]
        }
    }
    return [begin_rendering, surface_update, data_model_update]

def render_confirmation(data: ConfirmationData, base_url: str) -> List[Dict[str, Any]]:
    surface_id = "confirmation"
    begin_rendering = {
        "beginRendering": {
            "surfaceId": surface_id,
            "root": "confirmation-card",
            "styles": {"primaryColor": "#007BFF", "font": "Roboto"}
        }
    }

    components = [
        {"id": "confirmation-card", "component": {"Card": {"child": "confirmation-column"}}},
        {"id": "confirmation-column", "component": {"Column": {"children": {"explicitList": ["confirm-title", "confirm-image", "divider1", "confirm-details", "divider2", "confirm-dietary", "divider3", "confirm-text"]}}}},
        {"id": "confirm-title", "component": {"Text": {"usageHint": "h2", "text": {"path": "/title"}}}},
        {"id": "confirm-image", "component": {"Image": {"url": {"path": "/imageUrl"}}}},
        {"id": "confirm-details", "component": {"Text": {"text": {"path": "/bookingDetails"}}}},
        {"id": "confirm-dietary", "component": {"Text": {"text": {"path": "/dietaryRequirements"}}}},
        {"id": "confirm-text", "component": {"Text": {"usageHint": "h5", "text": {"literalString": "We look forward to seeing you!"}}}},
        {"id": "divider1", "component": {"Divider": {}}},
        {"id": "divider2", "component": {"Divider": {}}},
        {"id": "divider3", "component": {"Divider": {}}}
    ]

    surface_update = {
        "surfaceUpdate": {
            "surfaceId": surface_id,
            "components": components
        }
    }

    data_model_update = {
        "dataModelUpdate": {
            "surfaceId": surface_id,
            "path": "/",
            "contents": [
                {"key": "title", "valueString": f"Booking at {data.restaurantName}"},
                {"key": "bookingDetails", "valueString": f"{data.partySize} people at {data.reservationTime}"},
                {"key": "dietaryRequirements", "valueString": f"Dietary Requirements: {data.dietaryRequirements}"},
                {"key": "imageUrl", "valueString": data.imageUrl}
            ]
        }
    }
    return [begin_rendering, surface_update, data_model_update]
