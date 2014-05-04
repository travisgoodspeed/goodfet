/*! \file app.h
 *  \author Dave Huseby
 *  \brief basic types for defining a firmware app
 */

#ifndef APP_H
#define APP_H

// this is the prototype for all app "handle" functions
typedef void (*handle_fn)(uint8_t app,
			  uint8_t verb,
			  uint32_t len);

// Each app must declare one of these
typedef struct app_
{
	uint8_t const		app;		/* app number */
	handle_fn const		handle;		/* handle fn ptr */
	char const * const	name;		/* name of the app */
	char const * const	desc;		/* app description */
} app_t;

// The following externs give all apps access to the app list

// Global list of app_t's for all compiled in apps
extern app_t const * const apps[];

// Global number of apps in the app list
extern int const num_apps;

#endif

