import React from 'react';
import { Card, CardContent } from '../ui/Card';
import { Calendar, Clock } from 'lucide-react';

const TimelineTab = ({ timelineData }) => {
  if (!timelineData || timelineData.length === 0) {
    return (
      <Card className="mt-6">
        <CardContent className="p-12 text-center text-slate-500">
          No timeline data available for this case.
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="mt-6">
      <CardContent className="p-8">
        <div className="relative border-l-2 border-primary-200 ml-3 md:ml-6 space-y-8">
          {timelineData.map((event, index) => (
            <div key={index} className="relative pl-8 md:pl-10">
              <span className="absolute -left-3.5 flex h-7 w-7 items-center justify-center rounded-full bg-primary-100 ring-8 ring-white">
                <Calendar className="h-4 w-4 text-primary-600" />
              </span>
              <div className="flex flex-col flex-1 gap-1">
                <div className="flex items-center gap-2 text-sm text-slate-500 mb-1">
                  <Clock className="h-4 w-4" />
                  <time dateTime={event.date}>{event.date || 'Unknown Date'}</time>
                </div>
                <h3 className="text-lg font-semibold text-slate-900">{event.event}</h3>
                {event.description && <p className="text-slate-600 mt-2">{event.description}</p>}
                {event.related_drugs && Array.isArray(event.related_drugs) && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {event.related_drugs.map((drug, idx) => (
                      <span key={idx} className="inline-flex items-center rounded-md bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700 ring-1 ring-inset ring-blue-700/10">
                        {drug}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default TimelineTab;
