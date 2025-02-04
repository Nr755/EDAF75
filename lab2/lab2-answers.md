## Which relations have natural keys?
Several of the relations have natural keys:  
- **Customers**: They have unique usernames.  
- **Movies**: They have IMDb keys.  
- **Theaters**: They have unique names.  

---

## Is there a risk that any of the natural keys will ever change?
- For both **customers** and **theaters**, there is always the potential for a name change.  
- For **movies**, the IMDb keys are permanent and do not change.  

---

## Are there any weak entity sets?
A **weak entity** is one that cannot exist on its own and must be linked to another entity.  
- **Tickets** are a weak entity because a ticket **cannot exist without a screening**.  
- **Screenings** might seem like a weak entity at first, but they exist independently, even if no tickets are sold. Therefore, **screening is not a weak entity**.  

---

## In which relations do you want to use an invented key? Why?
We use an **invented key** (`id`) in both `screening` and `tickets`:  
- **Screening (`id`)**: Instead of using `(theatre, imdb_key, date, start_time)` as a composite key, we use `randomblob(16)` to generate a unique identifier.  
- **Ticket (`id`)**: Since a ticket must be uniquely identifiable, we also use `randomblob(16)` to create a unique identifier for each ticket.  

---

### Relational Model

customers(_username_, full_name, password)

movies(_imdb_key_, title, year, run_time)

theaters(_name_, capacity)

screening(_id_, start_time, /theatre/, date, /imdb_key/)

tickets(_id_, /username/, /date_and_time/)

---

### Two methods

## Tracking Available Seats for Each Performance

The first method is to have the available seat count directly in the `screening` table. This requires adding a column, `available_seats` or something similar, which is updated whenever a ticket is sold or canceled. When a customer purchases a ticket, we decreases the `available_seats` count. If a ticket is canceled, the count increases. This approach is efficient as it only requires selecting a single value. However, there's a risk if multiple users attempt to book at the same time or if a transaction fails, so we have to be able to avoid race conditions.

The second method calculates available seats dynamically by counting the number of tickets sold and subtracting that number from the theater’s total capacity. Instead of storing the available seat count, a query retrieves the number of booked tickets for a screening and subtracts it from the theater’s total seats. This method takes away the risk mentioned before since the count is always based on actual data. However, it's more expensive computationally, as every availability check requires counting rows in the `tickets` table and performing joins.

First one is more efficient but it requires proper transaction handling. Second one is safer at the cost of increased query complexity. It's a matter of what we have at our disposal and what the priority is.